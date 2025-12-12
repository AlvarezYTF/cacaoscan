"""
Django management command to train the binary cacao classifier.

This command trains a CNN classifier to distinguish between images
that contain cacao beans and images that don't.

Usage:
    python manage.py train_cacao_classifier --positive_dir /path/to/cacao/images --negative_dir /path/to/other/images
"""
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
import numpy as np
from typing import List, Tuple

from ml.classification.cacao_classifier import CacaoBinaryClassifier
from ml.utils.paths import get_artifacts_dir, ensure_dir_exists
from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.training.classifier")


class CacaoDataset(Dataset):
    """Dataset for binary classification (cacao / not_cacao)."""
    
    def __init__(self, positive_dir: Path, negative_dir: Path, transform=None):
        """
        Initialize dataset.
        
        Args:
            positive_dir: Directory with cacao bean images
            negative_dir: Directory with non-cacao images
            transform: Image transformations
        """
        self.transform = transform or self._default_transform()
        
        # Load positive examples (cacao)
        positive_images = list(positive_dir.glob("*.jpg")) + list(positive_dir.glob("*.png"))
        positive_images += list(positive_dir.glob("*.jpeg")) + list(positive_dir.glob("*.bmp"))
        
        # Load negative examples (not cacao)
        negative_images = list(negative_dir.glob("*.jpg")) + list(negative_dir.glob("*.png"))
        negative_images += list(negative_dir.glob("*.jpeg")) + list(negative_dir.glob("*.bmp"))
        
        # Create labels: 0 = not_cacao, 1 = cacao
        self.images = [(img, 1) for img in positive_images] + [(img, 0) for img in negative_images]
        
        logger.info(
            f"Dataset cargado: {len(positive_images)} imágenes de cacao, "
            f"{len(negative_images)} imágenes no-cacao, total: {len(self.images)}"
        )
    
    def _default_transform(self):
        """Default image transformations."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path, label = self.images[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            logger.error(f"Error cargando imagen {img_path}: {e}")
            # Return a black image as fallback
            return torch.zeros(3, 224, 224), label


class Command(BaseCommand):
    help = 'Train binary classifier for cacao bean detection'

    def add_arguments(self, parser):
        parser.add_argument(
            '--positive_dir',
            type=str,
            required=True,
            help='Directory containing positive examples (cacao bean images)'
        )
        parser.add_argument(
            '--negative_dir',
            type=str,
            required=True,
            help='Directory containing negative examples (non-cacao images)'
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=20,
            help='Number of training epochs (default: 20)'
        )
        parser.add_argument(
            '--batch_size',
            type=int,
            default=None,
            help='Batch size for training (default: auto - 32 for GPU, 16 for CPU)'
        )
        parser.add_argument(
            '--learning_rate',
            type=float,
            default=0.001,
            help='Learning rate (default: 0.001)'
        )
        parser.add_argument(
            '--output_path',
            type=str,
            default=None,
            help='Output path for the trained model (default: ml/artifacts/cacao_classifier.pt)'
        )
        parser.add_argument(
            '--device',
            type=str,
            choices=['cpu', 'cuda', 'auto'],
            default='auto',
            help='Device for training: cpu, cuda (GPU), or auto (detect automatically). Default: auto'
        )
        parser.add_argument(
            '--mixed_precision',
            action='store_true',
            help='Use mixed precision training (requires NVIDIA GPU with Tensor Cores)'
        )
        parser.add_argument(
            '--num_workers',
            type=int,
            default=None,
            help='Number of data loader workers (default: auto based on device)'
        )

    def _determine_device(self, device_option: str) -> torch.device:
        """
        Determine the device to use for training.
        
        Args:
            device_option: 'cpu', 'cuda', or 'auto'
            
        Returns:
            torch.device instance
        """
        if device_option == 'auto':
            if torch.cuda.is_available():
                device = torch.device('cuda')
                device_name = torch.cuda.get_device_name(0)
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"🚀 GPU detectada: {device_name} ({memory_gb:.1f} GB)"
                    )
                )
            else:
                device = torch.device('cpu')
                self.stdout.write(
                    self.style.WARNING("🖥️  GPU no disponible, usando CPU")
                )
        elif device_option == 'cuda':
            if not torch.cuda.is_available():
                self.stdout.write(
                    self.style.ERROR("⚠️  GPU solicitada pero no disponible, usando CPU")
                )
                device = torch.device('cpu')
            else:
                device = torch.device('cuda')
                device_name = torch.cuda.get_device_name(0)
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"🚀 Usando GPU: {device_name} ({memory_gb:.1f} GB)"
                    )
                )
        else:
            device = torch.device('cpu')
            self.stdout.write("🖥️  Usando CPU")
        
        return device
    
    def _optimize_batch_size(self, device: torch.device, initial_batch_size: int) -> int:
        """
        Optimize batch size based on available GPU memory.
        
        Args:
            device: torch.device instance
            initial_batch_size: Initial batch size
            
        Returns:
            Optimized batch size
        """
        if device.type == 'cuda':
            memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            # Adjust batch size based on GPU memory
            if memory_gb >= 8:
                # High-end GPU (RTX 3070, 3080, etc.)
                optimized = max(initial_batch_size, 64)
            elif memory_gb >= 6:
                # Mid-range GPU (RTX 3060, etc.)
                optimized = max(initial_batch_size, 32)
            elif memory_gb >= 4:
                # Entry-level GPU (GTX 1660, etc.)
                optimized = max(initial_batch_size, 16)
            else:
                # Low memory GPU
                optimized = min(initial_batch_size, 16)
            
            if optimized != initial_batch_size:
                self.stdout.write(
                    f"  📊 Batch size optimizado: {initial_batch_size} -> {optimized} "
                    f"(basado en memoria GPU: {memory_gb:.1f} GB)"
                )
            
            return optimized
        
        return initial_batch_size

    def handle(self, *args, **options):
        positive_dir = Path(options['positive_dir'])
        negative_dir = Path(options['negative_dir'])
        epochs = options['epochs']
        batch_size = options['batch_size']
        learning_rate = options['learning_rate']
        device_option = options['device']
        use_mixed_precision = options['mixed_precision']
        num_workers = options['num_workers']
        
        # Validate directories
        if not positive_dir.exists():
            raise CommandError(f"Directory not found: {positive_dir}")
        if not negative_dir.exists():
            raise CommandError(f"Directory not found: {negative_dir}")
        
        # Determine output path
        if options['output_path']:
            output_path = Path(options['output_path'])
        else:
            artifacts_dir = get_artifacts_dir()
            ensure_dir_exists(artifacts_dir)
            output_path = artifacts_dir / "cacao_classifier.pt"
        
        # Determine device
        device = self._determine_device(device_option)
        
        # Set default batch size if not provided
        if batch_size is None:
            if device.type == 'cuda':
                batch_size = 32  # Default for GPU
            else:
                batch_size = 16  # Default for CPU (smaller for better performance)
        
        # Optimize batch size for GPU
        if device.type == 'cuda':
            batch_size = self._optimize_batch_size(device, batch_size)
        elif device.type == 'cpu':
            # For CPU, use smaller batch size for better performance
            if batch_size > 16:
                self.stdout.write(
                    f"  📊 Batch size ajustado para CPU: {batch_size} -> 16 "
                    f"(CPU funciona mejor con batches más pequeños)"
                )
                batch_size = 16
        
        # Determine number of workers
        if num_workers is None:
            if device.type == 'cuda':
                num_workers = 4  # More workers for GPU
            else:
                num_workers = 2  # Fewer workers for CPU
        
        # Validate mixed precision
        if use_mixed_precision and device.type != 'cuda':
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Mixed precision requiere GPU, desactivando..."
                )
            )
            use_mixed_precision = False
        
        self.stdout.write(f"\n📋 Configuración de entrenamiento:")
        self.stdout.write(f"  Imágenes positivas: {positive_dir}")
        self.stdout.write(f"  Imágenes negativas: {negative_dir}")
        self.stdout.write(f"  Épocas: {epochs}")
        self.stdout.write(f"  Batch size: {batch_size}")
        self.stdout.write(f"  Learning rate: {learning_rate}")
        self.stdout.write(f"  Dispositivo: {device}")
        self.stdout.write(f"  Workers: {num_workers}")
        self.stdout.write(f"  Mixed precision: {'✅' if use_mixed_precision else '❌'}")
        self.stdout.write(f"  Modelo de salida: {output_path}\n")
        
        # Create dataset
        dataset = CacaoDataset(positive_dir, negative_dir)
        
        if len(dataset) == 0:
            raise CommandError("No se encontraron imágenes en los directorios especificados")
        
        # Split dataset (80% train, 20% validation)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        
        # Create data loaders with GPU optimizations
        pin_memory = device.type == 'cuda'
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=num_workers > 0
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=num_workers > 0
        )
        
        # Initialize model
        model = CacaoBinaryClassifier(num_classes=2)
        model.to(device)
        
        # Enable mixed precision scaler if requested
        scaler = None
        autocast_context = None
        if use_mixed_precision:
            from torch.cuda.amp import GradScaler, autocast
            scaler = GradScaler()
            autocast_context = autocast
            self.stdout.write("  ✅ Mixed precision training activado\n")
        else:
            # Dummy context manager for when mixed precision is disabled
            from contextlib import nullcontext
            autocast_context = nullcontext
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
        
        # Training loop
        best_val_acc = 0.0
        
        self.stdout.write(f"\n🚀 Iniciando entrenamiento...\n")
        
        for epoch in range(epochs):
            # Training phase
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for batch_idx, (images, labels) in enumerate(train_loader):
                images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
                
                optimizer.zero_grad()
                
                if use_mixed_precision and scaler:
                    # Mixed precision forward pass
                    with autocast_context():
                        outputs = model(images)
                        loss = criterion(outputs, labels)
                    
                    # Mixed precision backward pass
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    # Standard precision
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                
                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
                
                # Show progress every 10 batches
                if (batch_idx + 1) % 10 == 0:
                    current_acc = 100 * train_correct / train_total
                    self.stdout.write(
                        f"  Batch {batch_idx+1}/{len(train_loader)}: "
                        f"Loss: {loss.item():.4f}, Acc: {current_acc:.2f}%",
                        ending='\r'
                    )
            
            # Validation phase
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
                    
                    if use_mixed_precision:
                        with autocast_context():
                            outputs = model(images)
                            loss = criterion(outputs, labels)
                    else:
                        outputs = model(images)
                        loss = criterion(outputs, labels)
                    
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()
            
            train_acc = 100 * train_correct / train_total
            val_acc = 100 * val_correct / val_total
            
            # Clear progress line and print epoch results
            self.stdout.write(' ' * 80 + '\r', ending='')
            self.stdout.write(
                f"Época {epoch+1}/{epochs}: "
                f"Train Loss: {train_loss/len(train_loader):.4f}, Train Acc: {train_acc:.2f}% | "
                f"Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_acc:.2f}%"
            )
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), output_path)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Mejor modelo guardado (val_acc: {val_acc:.2f}%)")
                )
            
            scheduler.step()
            
            # Show GPU memory usage if using GPU
            if device.type == 'cuda':
                memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
                memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
                self.stdout.write(
                    f"  💾 GPU Memory: {memory_allocated:.2f} GB / {memory_reserved:.2f} GB"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Entrenamiento completado!\n'
                f'Mejor precisión de validación: {best_val_acc:.2f}%\n'
                f'Modelo guardado en: {output_path}'
            )
        )

