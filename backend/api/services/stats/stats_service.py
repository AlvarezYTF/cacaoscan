"""
Statistics service for CacaoScan API.
"""
import logging
from datetime import timedelta
from typing import Dict, Any, List, Tuple
from django.db.models import Q, Count, Avg, F, Case, When, IntegerField
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..base import BaseService

User = get_user_model()

logger = logging.getLogger("cacaoscan.services.stats")


class StatsService(BaseService):
    """
    Service for generating system statistics.
    """
    
    def __init__(self):
        super().__init__()
        try:
            from ...utils.model_imports import get_models_safely
            
            models = get_models_safely({
                'CacaoImage': 'images_app.models.CacaoImage',
                'CacaoPrediction': 'images_app.models.CacaoPrediction',
                'Finca': 'fincas_app.models.Finca'
            })
            self.CacaoImage = models.get('CacaoImage')
            self.CacaoPrediction = models.get('CacaoPrediction')
            self.Finca = models.get('Finca')
        except Exception as e:
            logger.error(f"Error inicializando StatsService: {e}", exc_info=True)
            self.CacaoImage = None
            self.CacaoPrediction = None
            self.Finca = None
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            Dictionary with user statistics
        """
        try:
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            staff_users = User.objects.filter(is_staff=True).count()
            superusers = User.objects.filter(is_superuser=True).count()
            
            self.log_info(f"Usuarios - Total: {total_users}, Activos: {active_users}, Staff: {staff_users}, Superusers: {superusers}")
            
            try:
                analyst_users = User.objects.filter(groups__name='analyst').distinct().count()
            except Exception as e:
                self.log_warning(f"Error obteniendo analyst users: {e}")
                analyst_users = 0
            
            try:
                farmer_users = User.objects.filter(
                    ~Q(is_superuser=True),
                    ~Q(is_staff=True),
                    ~Q(groups__name='analyst')
                ).count()
            except Exception as e:
                self.log_warning(f"Error obteniendo farmer users: {e}")
                farmer_users = 0
            
            # Try different possible relationship names for verified users
            verified_users = 0
            try:
                verified_users = User.objects.filter(auth_email_token__is_verified=True).count()
            except Exception as e1:
                self.log_warning(f"Error con auth_email_token, intentando email_verification_token: {e1}")
                try:
                    verified_users = User.objects.filter(email_verification_token__is_verified=True).count()
                except Exception as e2:
                    self.log_warning(f"Error con email_verification_token también: {e2}")
                    # Fallback: use is_active as proxy for verified
                    verified_users = User.objects.filter(is_active=True).count()
            
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            try:
                users_this_week = User.objects.filter(date_joined__date__gte=this_week).count()
            except Exception as e:
                self.log_warning(f"Error obteniendo users_this_week: {e}")
                users_this_week = 0
            
            try:
                users_this_month = User.objects.filter(date_joined__date__gte=this_month).count()
            except Exception as e:
                self.log_warning(f"Error obteniendo users_this_month: {e}")
                users_this_month = 0
            
            return {
                'total': total_users,
                'active': active_users,
                'staff': staff_users,
                'superusers': superusers,
                'analysts': analyst_users,
                'farmers': farmer_users,
                'verified': verified_users,
                'this_week': users_this_week,
                'this_month': users_this_month
            }
        except Exception as e:
            self.log_error(f"Error crítico en get_user_stats: {e}")
            logger.error(f"Error crítico en get_user_stats: {e}", exc_info=True)
            # Return minimal stats instead of failing completely
            return {
                'total': 0,
                'active': 0,
                'staff': 0,
                'superusers': 0,
                'analysts': 0,
                'farmers': 0,
                'verified': 0,
                'this_week': 0,
                'this_month': 0
            }
    
    def get_image_stats(self) -> Dict[str, Any]:
        """
        Get image statistics.
        
        Returns:
            Dictionary with image statistics
        """
        if self.CacaoImage is None:
            return {
                'total': 0,
                'processed': 0,
                'unprocessed': 0,
                'this_week': 0,
                'this_month': 0,
                'processing_rate': 0
            }
        
        try:
            total_images = self.CacaoImage.objects.count()
            processed_images = self.CacaoImage.objects.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            self.log_info(f"Imágenes - Total: {total_images}, Procesadas: {processed_images}, Sin procesar: {unprocessed_images}")
            
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            try:
                images_this_week = self.CacaoImage.objects.filter(created_at__date__gte=this_week).count()
            except Exception as e:
                self.log_warning(f"Error obteniendo images_this_week: {e}")
                images_this_week = 0
            
            try:
                images_this_month = self.CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            except Exception as e:
                self.log_warning(f"Error obteniendo images_this_month: {e}")
                images_this_month = 0
            
            processing_rate = round((processed_images / total_images * 100), 2) if total_images > 0 else 0
            
            return {
                'total': total_images,
                'processed': processed_images,
                'unprocessed': unprocessed_images,
                'this_week': images_this_week,
                'this_month': images_this_month,
                'processing_rate': processing_rate
            }
        except Exception as e:
            self.log_error(f"Error crítico en get_image_stats: {e}")
            logger.error(f"Error crítico en get_image_stats: {e}", exc_info=True)
            return {
                'total': 0,
                'processed': 0,
                'unprocessed': 0,
                'this_week': 0,
                'this_month': 0,
                'processing_rate': 0
            }
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Get prediction statistics.
        
        Returns:
            Dictionary with prediction statistics
        """
        if self.CacaoPrediction is None:
            return {
                'total': 0,
                'average_dimensions': {
                    'alto_mm': 0,
                    'ancho_mm': 0,
                    'grosor_mm': 0,
                    'peso_g': 0
                },
                'average_confidence': 0,
                'average_processing_time_ms': 0
            }
        
        total_predictions = self.CacaoPrediction.objects.count()
        
        # Calculate average_confidence using SQL aggregation
        # average_confidence = (confidence_alto + confidence_ancho + confidence_grosor + confidence_peso) / 4
        avg_confidence_expr = (
            F('confidence_alto') + F('confidence_ancho') + 
            F('confidence_grosor') + F('confidence_peso')
        ) / 4
        
        avg_dimensions = self.CacaoPrediction.objects.aggregate(
            avg_alto=Avg('alto_mm'),
            avg_ancho=Avg('ancho_mm'),
            avg_grosor=Avg('grosor_mm'),
            avg_peso=Avg('peso_g'),
            avg_processing_time=Avg('processing_time_ms'),
            avg_confidence=Avg(avg_confidence_expr)
        )
        
        avg_confidence = float(avg_dimensions.get('avg_confidence', 0) or 0)
        
        # Calculate quality distribution using SQL aggregations
        # Annotate each prediction with its average_confidence
        queryset = self.CacaoPrediction.objects.annotate(
            avg_conf=avg_confidence_expr
        )
        
        quality_distribution = {
            'excelente': queryset.filter(avg_conf__gte=0.8).count(),
            'buena': queryset.filter(avg_conf__gte=0.6, avg_conf__lt=0.8).count(),
            'regular': queryset.filter(avg_conf__gte=0.4, avg_conf__lt=0.6).count(),
            'baja': queryset.filter(avg_conf__lt=0.4).count()
        }
        
        self.log_info(f"Distribución de calidad: {quality_distribution}")
        
        return {
            'total': total_predictions,
            'average_dimensions': {
                'alto_mm': round(float(avg_dimensions.get('avg_alto', 0) or 0), 2),
                'ancho_mm': round(float(avg_dimensions.get('avg_ancho', 0) or 0), 2),
                'grosor_mm': round(float(avg_dimensions.get('avg_grosor', 0) or 0), 2),
                'peso_g': round(float(avg_dimensions.get('avg_peso', 0) or 0), 2)
            },
            'average_confidence': round(float(avg_confidence), 3),
            'average_processing_time_ms': round(float(avg_dimensions.get('avg_processing_time', 0) or 0), 0),
            'quality_distribution': quality_distribution
        }
    
    def get_activity_by_day(self, max_days: int = 30) -> Dict[str, Any]:
        """
        Get activity statistics by day.
        
        Args:
            max_days: Maximum number of days to check
            
        Returns:
            Dictionary with activity by day data
        """
        today = timezone.now().date()
        
        images_by_date = {}
        if self.CacaoImage is not None:
            images_by_date = dict(
                self.CacaoImage.objects
                .filter(created_at__date__gte=today - timedelta(days=max_days))
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .values_list('date', 'count')
            )
        
        users_by_date = dict(
            User.objects
            .filter(date_joined__date__gte=today - timedelta(days=max_days))
            .annotate(date=TruncDate('date_joined'))
            .values('date')
            .annotate(count=Count('id'))
            .values_list('date', 'count')
        )
        
        predictions_by_date = {}
        if self.CacaoPrediction is not None:
            predictions_by_date = dict(
                self.CacaoPrediction.objects
                .filter(created_at__date__gte=today - timedelta(days=max_days))
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .values_list('date', 'count')
            )
        
        all_dates_with_activity = set()
        all_dates_with_activity.update(images_by_date.keys())
        all_dates_with_activity.update(users_by_date.keys())
        all_dates_with_activity.update(predictions_by_date.keys())
        
        days_with_activity_count = len(all_dates_with_activity)
        
        if days_with_activity_count > 10:
            days_to_show = max_days
            self.log_info(f"Más de 10 días con actividad ({days_with_activity_count}), mostrando últimos {days_to_show} días")
        else:
            days_to_show = 7
            self.log_info(f"{days_with_activity_count} días con actividad, mostrando últimos 7 días")
        
        activity_by_day = []
        activity_labels = []
        
        for i in range(days_to_show - 1, -1, -1):
            date = today - timedelta(days=i)
            
            images_count = images_by_date.get(date, 0)
            users_count = users_by_date.get(date, 0)
            predictions_count = predictions_by_date.get(date, 0)
            
            total_activity = images_count + users_count + predictions_count
            activity_by_day.append(total_activity)
            
            if i == 0:
                activity_labels.append('Hoy')
            elif i == 1:
                activity_labels.append('Ayer')
            else:
                if days_to_show > 14:
                    activity_labels.append(date.strftime('%d/%m'))
                else:
                    day_names = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
                    day_name = day_names[date.weekday()]
                    activity_labels.append(f"{day_name} {date.strftime('%d/%m')}")
        
        self.log_info(f"Actividad por día: {activity_by_day} ({len(activity_by_day)} días mostrados)")
        
        return {
            'labels': activity_labels,
            'data': activity_by_day
        }
    
    def get_finca_stats(self) -> Dict[str, Any]:
        """
        Get finca statistics.
        
        Returns:
            Dictionary with finca statistics
        """
        if self.Finca is None:
            self.log_warning("Finca model no está disponible")
            return {
                'total': 0,
                'this_week': 0,
                'this_month': 0
            }
        
        try:
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            total_fincas = self.Finca.objects.count()
            
            # Try different date fields that might exist
            fincas_this_week = 0
            fincas_this_month = 0
            
            try:
                # Try fecha_registro first
                fincas_this_week = self.Finca.objects.filter(fecha_registro__date__gte=this_week).count()
                fincas_this_month = self.Finca.objects.filter(fecha_registro__date__gte=this_month).count()
            except Exception as e:
                self.log_warning(f"Error con fecha_registro, intentando created_at: {e}")
                try:
                    # Fallback to created_at
                    fincas_this_week = self.Finca.objects.filter(created_at__date__gte=this_week).count()
                    fincas_this_month = self.Finca.objects.filter(created_at__date__gte=this_month).count()
                except Exception as e2:
                    self.log_warning(f"Error con created_at también: {e2}")
                    # If both fail, just return total
                    fincas_this_week = 0
                    fincas_this_month = 0
            
            self.log_info(f"Fincas - Total: {total_fincas}, Esta semana: {fincas_this_week}, Este mes: {fincas_this_month}")
            
            return {
                'total': total_fincas,
                'this_week': fincas_this_week,
                'this_month': fincas_this_month
            }
        except Exception as e:
            self.log_error(f"Error crítico obteniendo estadísticas de fincas: {e}")
            logger.error(f"Error crítico obteniendo estadísticas de fincas: {e}", exc_info=True)
            return {
                'total': 0,
                'this_week': 0,
                'this_month': 0
            }
    
    def get_top_regions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top regions by image count.
        
        Args:
            limit: Maximum number of regions to return
            
        Returns:
            List of region statistics
        """
        if self.CacaoImage is None:
            return []
        
        return list(
            self.CacaoImage.objects.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:limit]
        )
    
    def get_top_fincas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top fincas by image count.
        
        Args:
            limit: Maximum number of fincas to return
            
        Returns:
            List of finca statistics
        """
        if self.CacaoImage is None:
            return []
        
        return list(
            self.CacaoImage.objects.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:limit]
        )
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get all system statistics.
        
        Returns:
            Dictionary with all statistics
        """
        try:
            # Get each stat category separately to handle individual failures
            try:
                user_stats = self.get_user_stats()
                self.log_info(f"User stats obtenidas: {user_stats}")
            except Exception as e:
                self.log_error(f"Error crítico obteniendo user stats: {e}")
                logger.error(f"Error crítico obteniendo user stats: {e}", exc_info=True)
                user_stats = {
                    'total': 0,
                    'active': 0,
                    'staff': 0,
                    'superusers': 0,
                    'analysts': 0,
                    'farmers': 0,
                    'verified': 0,
                    'this_week': 0,
                    'this_month': 0
                }
            
            try:
                image_stats = self.get_image_stats()
                self.log_info(f"Image stats obtenidas: {image_stats}")
            except Exception as e:
                self.log_error(f"Error crítico obteniendo image stats: {e}")
                logger.error(f"Error crítico obteniendo image stats: {e}", exc_info=True)
                image_stats = {
                    'total': 0,
                    'processed': 0,
                    'unprocessed': 0,
                    'this_week': 0,
                    'this_month': 0,
                    'processing_rate': 0
                }
            
            prediction_stats = {}
            try:
                prediction_stats = self.get_prediction_stats()
                self.log_info(f"Prediction stats obtenidas")
            except Exception as e:
                self.log_warning(f"Error obteniendo prediction stats: {e}")
                prediction_stats = {
                    'total': 0,
                    'average_dimensions': {'alto_mm': 0, 'ancho_mm': 0, 'grosor_mm': 0, 'peso_g': 0},
                    'average_confidence': 0,
                    'average_processing_time_ms': 0
                }
            
            activity_by_day = {}
            try:
                activity_by_day = self.get_activity_by_day()
                self.log_info(f"Activity by day obtenida")
            except Exception as e:
                self.log_warning(f"Error obteniendo activity by day: {e}")
                activity_by_day = {'labels': [], 'data': []}
            
            try:
                finca_stats = self.get_finca_stats()
                self.log_info(f"Finca stats obtenidas: {finca_stats}")
            except Exception as e:
                self.log_error(f"Error crítico obteniendo finca stats: {e}")
                logger.error(f"Error crítico obteniendo finca stats: {e}", exc_info=True)
                finca_stats = {
                    'total': 0,
                    'this_week': 0,
                    'this_month': 0
                }
            
            top_regions = []
            top_fincas = []
            try:
                top_regions = self.get_top_regions()
                top_fincas = self.get_top_fincas()
            except Exception as e:
                self.log_warning(f"Error obteniendo top regions/fincas: {e}")
            
            # Ensure all required stats are dictionaries BEFORE extracting quality_distribution
            if not isinstance(user_stats, dict):
                user_stats = {'total': 0, 'active': 0, 'staff': 0, 'superusers': 0, 'analysts': 0, 'farmers': 0, 'verified': 0, 'this_week': 0, 'this_month': 0}
            if not isinstance(image_stats, dict):
                image_stats = {'total': 0, 'processed': 0, 'unprocessed': 0, 'this_week': 0, 'this_month': 0, 'processing_rate': 0}
            if not isinstance(finca_stats, dict):
                finca_stats = {'total': 0, 'this_week': 0, 'this_month': 0}
            if not isinstance(prediction_stats, dict):
                prediction_stats = {'total': 0, 'average_dimensions': {'alto_mm': 0, 'ancho_mm': 0, 'grosor_mm': 0, 'peso_g': 0}, 'average_confidence': 0, 'average_processing_time_ms': 0}
            if not isinstance(activity_by_day, dict):
                activity_by_day = {'labels': [], 'data': []}
            
            # Safely extract quality_distribution from prediction_stats (now guaranteed to be a dict)
            quality_distribution = prediction_stats.pop('quality_distribution', {
                'excelente': 0,
                'buena': 0,
                'regular': 0,
                'baja': 0
            })
            
            stats = {
                'users': user_stats,
                'images': image_stats,
                'fincas': finca_stats,
                'predictions': prediction_stats,
                'top_regions': top_regions if isinstance(top_regions, list) else [],
                'top_fincas': top_fincas if isinstance(top_fincas, list) else [],
                'activity_by_day': activity_by_day,
                'quality_distribution': quality_distribution,
                'generated_at': timezone.now().isoformat()
            }
            
            self.log_info(
                f"Estadísticas generadas - Users: {stats['users'].get('total', 0)}, "
                f"Fincas: {stats['fincas'].get('total', 0)}, "
                f"Images: {stats['images'].get('total', 0)}, "
                f"Quality: {stats['predictions'].get('average_confidence', 0)}"
            )
            
            return stats
        except Exception as e:
            self.log_error(f"Error crítico obteniendo estadísticas del sistema: {e}")
            logger.error(f"Error crítico obteniendo estadísticas del sistema: {e}", exc_info=True)
            # Don't re-raise, return empty stats instead to prevent 500 error
            return self.get_empty_stats()
    
    def get_empty_stats(self) -> Dict[str, Any]:
        """
        Get empty statistics structure.
        
        Returns:
            Dictionary with empty statistics
        """
        return {
            'users': {
                'total': 0,
                'active': 0,
                'staff': 0,
                'superusers': 0,
                'analysts': 0,
                'farmers': 0,
                'verified': 0,
                'this_week': 0,
                'this_month': 0
            },
            'images': {
                'total': 0,
                'processed': 0,
                'unprocessed': 0,
                'this_week': 0,
                'this_month': 0,
                'processing_rate': 0
            },
            'predictions': {
                'total': 0,
                'average_dimensions': {
                    'alto_mm': 0,
                    'ancho_mm': 0,
                    'grosor_mm': 0,
                    'peso_g': 0
                },
                'average_confidence': 0,
                'average_processing_time_ms': 0
            },
            'fincas': {
                'total': 0,
                'this_week': 0,
                'this_month': 0
            },
            'top_regions': [],
            'top_fincas': [],
            'activity_by_day': {
                'labels': [],
                'data': []
            },
            'quality_distribution': {
                'excelente': 0,
                'buena': 0,
                'regular': 0,
                'baja': 0
            },
            'generated_at': timezone.now().isoformat()
        }

