from django.core.management.base import BaseCommand
from catalogos.models import Departamento, Municipio


class Command(BaseCommand):
    help = "Cargar todos los departamentos y municipios de Colombia"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de departamentos y municipios de Colombia...'))

        # Datos completos de Colombia (32 departamentos + BogotÃ¡ D.C.)
        data = {
            "05": ("Antioquia", [
                "001", "MedellÃ­n", "002", "Bello", "003", "ItagÃ¼Ã­", "004", "Envigado",
                "005", "Rionegro", "008", "La Ceja", "009", "Marinilla", "011", "El Retiro",
                "013", "Guarne", "014", "GuatapÃ©", "015", "ConcepciÃ³n", "016", "AlejandrÃ­a",
                "017", "El Carmen de Viboral", "019", "Granada", "021", "Santuario",
                "023", "Porfirio Barba Jacob", "024", "Cisneros", "025", "Aguadas",
                "026", "Anserma", "027", "Aranzazu", "028", "Belmira", "029", "Betania",
                "031", "Betulia", "033", "BriceÃ±o", "034", "BuriticÃ¡", "035", "Caicedo",
                "036", "Caldas", "037", "Campamento", "038", "CaÃ±asgordas", "039", "CaracolÃ­",
                "040", "Caramanta", "041", "Carepa", "043", "Carolina", "044", "DonmatÃ­as",
                "045", "EbÃ©jico", "046", "El Bagre", "048", "EntrerrÃ­os", "049", "Epitacio",
                "051", "Fredonia", "052", "Frontino", "053", "Giraldo", "054", "Girardota",
                "055", "GÃ³mez Plata", "056", "Guadalupe", "057", "Heliconia", "059", "Hispania",
                "060", "Ituango", "062", "JericÃ³", "063", "La Estrella", "064", "La Pintada",
                "065", "La UniÃ³n", "066", "Liborina", "067", "Maceo", "069", "Montebello",
                "070", "MutatÃ¡", "071", "NariÃ±o", "072", "NechÃ­", "073", "NecoclÃ­",
                "074", "Olaya", "075", "Peque", "076", "Pueblorrico", "077", "Puerto BerrÃ­o",
                "078", "Puerto Nare", "079", "Puerto Triunfo", "080", "Remedios", "081", "Retiro",
                "082", "Rionegro", "084", "Sabanalarga", "085", "Sabaneta", "086", "Salgar",
                "087", "San AndrÃ©s", "088", "San Carlos", "089", "San Francisco", "090", "San JerÃ³nimo",
                "091", "San JosÃ© de la MontaÃ±a", "092", "San Juan de UrabÃ¡", "093", "San LuÃ­s",
                "094", "San Pedro", "095", "San Pedro de UrabÃ¡", "096", "San Rafael", "097", "San Roque",
                "098", "San Vicente", "099", "Santa BÃ¡rbara", "100", "Santa FÃ© de Antioquia",
                "101", "Santa Rosa de Osos", "102", "Santo Domingo", "103", "Santuario",
                "104", "Segovia", "105", "SonsÃ³n", "106", "SopetrÃ¡n", "107", "TÃ¡mesis",
                "108", "TarazÃ¡", "109", "Tarso", "110", "TitiribÃ­", "111", "Toledo",
                "112", "Turbo", "113", "Uramita", "114", "Urrao", "115", "Valdivia",
                "116", "ValparaÃ­so", "117", "VegachÃ­", "118", "Venecia", "119", "VigÃ­a del Fuerte",
                "121", "YalÃ­", "122", "Yarumal", "123", "YolombÃ³", "124", "YondÃ³",
                "125", "Zaragoza"
            ]),
            "08": ("AtlÃ¡ntico", [
                "001", "Barranquilla", "002", "Baranoa", "003", "Campo de la Cruz",
                "004", "Candelaria", "005", "Galapa", "006", "Juan de Acosta",
                "007", "Luruaco", "008", "Malambo", "009", "ManatÃ­",
                "010", "Palmar de Varela", "011", "PiojÃ³", "012", "Polonuevo",
                "013", "Ponedera", "014", "Puerto Colombia", "015", "RepelÃ³n",
                "016", "Sabanagrande", "017", "Sabanalarga", "018", "Santa LucÃ­a",
                "019", "Santo TomÃ¡s", "020", "Soledad", "021", "Suan",
                "022", "TubarÃ¡", "023", "UsiacurÃ­"
            ]),
            "11": ("BogotÃ¡ D.C.", [
                "001", "BogotÃ¡ D.C."
            ]),
            "13": ("BolÃ­var", [
                "001", "Cartagena", "002", "AchÃ­", "003", "Altos del Rosario",
                "004", "Arenal", "005", "Arjona", "006", "Arroyohondo",
                "007", "Barranco de Loba", "008", "Calamar", "009", "Cantagallo",
                "010", "Cicuco", "011", "CÃ³rdoba", "012", "Clemencia",
                "013", "El Carmen de BolÃ­var", "014", "El Guamo", "015", "El PeÃ±Ã³n",
                "016", "Hatonuevo", "017", "MaganguÃ©", "018", "Mahates",
                "019", "Margarita", "020", "MarÃ­a la Baja", "021", "MompÃ³s",
                "022", "Montecristo", "023", "Morales", "024", "NorosÃ­",
                "025", "Pinillos", "026", "Regidor", "027", "RÃ­o Viejo",
                "028", "San CristÃ³bal", "029", "San Estanislao", "030", "San Fernando",
                "031", "San Jacinto", "032", "San Jacinto del Cauca", "033", "San Juan Nepomuceno",
                "034", "San MartÃ­n de Loba", "035", "San Pablo", "036", "Santa Catalina",
                "037", "Santa Rosa", "038", "Santa Rosa del Sur", "039", "SimitÃ­",
                "040", "Soplaviento", "041", "Talaigua Nuevo", "042", "Tiquisio",
                "043", "Turbaco", "044", "TurbanÃ¡", "045", "Villanueva",
                "046", "Zambrano"
            ]),
            "15": ("BoyacÃ¡", [
                "001", "Tunja", "002", "Almeida", "003", "Aquitania",
                "004", "Arcabuco", "005", "BelÃ©n", "006", "Berbeo",
                "007", "BetÃ©itiva", "008", "Boavita", "009", "BoyacÃ¡",
                "010", "BriceÃ±o", "011", "Buenavista", "012", "BusbanzÃ¡",
                "013", "Caldas", "014", "Campohermoso", "015", "Cerinza",
                "016", "Chinavita", "017", "ChiquinquirÃ¡", "018", "Chiscas",
                "019", "Chita", "020", "Chitaraque", "021", "ChivatÃ¡",
                "022", "CiÃ©nega", "023", "CÃ³mbita", "024", "Coper",
                "025", "Corrales", "026", "CovarachÃ­a", "027", "CubarÃ¡",
                "028", "Cucaita", "029", "CuÃ­tiva", "030", "Duitama",
                "031", "El Cocuy", "032", "El Espino", "033", "Firavitoba",
                "034", "Floresta", "035", "GachantivÃ¡", "036", "GÃ¡meza",
                "037", "Garagoa", "038", "Guacamayas", "039", "Guateque",
                "040", "GuayatÃ¡", "041", "GÃ¼icÃ¡n", "042", "Iza",
                "043", "Jenesano", "044", "JericÃ³", "045", "Labranzagrande",
                "046", "La Capilla", "047", "La Victoria", "048", "La Uvita",
                "049", "Villa de Leyva", "050", "Macanal", "051", "MaripÃ­",
                "052", "Miraflores", "053", "Mongua", "054", "MonguÃ­",
                "055", "MoniquirÃ¡", "056", "Motavita", "057", "Muzo",
                "058", "Nobsa", "059", "Nuevo ColÃ³n", "060", "OicatÃ¡",
                "061", "Otanche", "062", "Pachavita", "063", "PÃ¡ez",
                "064", "Paipa", "065", "Pajarito", "066", "Panqueba",
                "067", "Pauna", "068", "Paya", "069", "Paz de RÃ­o",
                "070", "Pesca", "071", "Pisba", "072", "Puerto BoyacÃ¡",
                "073", "QuÃ­pama", "074", "RamiriquÃ­", "075", "RÃ¡quira",
                "076", "RondÃ³n", "077", "SaboyÃ¡", "078", "SÃ¡chica",
                "079", "SamacÃ¡", "080", "San Eduardo", "081", "San JosÃ© de Pare",
                "082", "San LuÃ­s de Gaceno", "083", "San Mateo", "084", "San Miguel de Sema",
                "085", "San Pablo de Borbur", "086", "Santana", "087", "Santa MarÃ­a",
                "088", "Santa Rosa de Viterbo", "089", "Santa SofÃ­a", "090", "Sativanorte",
                "091", "Sativasur", "092", "Siachoque", "093", "SoatÃ¡",
                "094", "Socha", "095", "SocotÃ¡", "096", "Sogamoso",
                "097", "Somondoco", "098", "Sora", "099", "SoracÃ¡",
                "100", "SotaquirÃ¡", "101", "SusacÃ³n", "102", "SutamarchÃ¡n",
                "103", "Sutatenza", "104", "Tasco", "105", "Tenza",
                "106", "TibanÃ¡", "107", "Tibasosa", "108", "TinjacÃ¡",
                "109", "Tipacoque", "110", "Toca", "111", "TogÃ¼Ã­",
                "112", "TÃ³paga", "113", "Tota", "114", "TununguÃ¡",
                "115", "TurmequÃ©", "116", "Tuta", "117", "TutazÃ¡",
                "118", "Ãšmbita", "119", "Ventaquemada", "120", "Villa de San Diego de UbatÃ©",
                "121", "ViracachÃ¡", "122", "Zetaquira"
            ]),
            "17": ("Caldas", [
                "001", "Manizales", "002", "Aguadas", "003", "Anserma",
                "004", "Aranzazu", "005", "BelalcÃ¡zar", "006", "ChinchinÃ¡",
                "007", "Filadelfia", "008", "La Dorada", "009", "La Merced",
                "010", "Manzanares", "011", "Marmato", "012", "Marquetalia",
                "013", "Marulanda", "014", "Neira", "015", "Norcasia",
                "016", "PÃ¡cora", "017", "Palestina", "018", "Pensilvania",
                "019", "Riosucio", "020", "Risaralda", "021", "Salamina",
                "022", "SamanÃ¡", "023", "San JosÃ©", "024", "SupÃ­a",
                "025", "Victoria", "026", "VillamarÃ­a", "027", "Viterbo"
            ]),
            "18": ("CaquetÃ¡", [
                "001", "Florencia", "002", "Albania", "003", "BelÃ©n de los Andaquies",
                "004", "Cartagena del ChairÃ¡", "005", "Curillo", "006", "El Doncello",
                "007", "El Paujil", "008", "La MontaÃ±ita", "009", "MilÃ¡n",
                "010", "Morelia", "011", "Puerto Rico", "012", "San JosÃ© del Fragua",
                "013", "San Vicente del CaguÃ¡n", "014", "Solano", "015", "Solita",
                "016", "ValparaÃ­so"
            ]),
            "19": ("Cauca", [
                "001", "PopayÃ¡n", "002", "Almaguer", "003", "Argelia",
                "004", "Balboa", "005", "BolÃ­var", "006", "Buenos Aires",
                "007", "CajibÃ­o", "008", "Caldono", "009", "Caloto",
                "010", "Corinto", "011", "El Tambo", "012", "Florencia",
                "013", "GuachenÃ©", "014", "Guapi", "015", "InzÃ¡",
                "016", "JambalÃ³", "017", "La Sierra", "018", "La Vega",
                "019", "LÃ³pez", "020", "Mercaderes", "021", "Miranda",
                "022", "Morales", "023", "Padilla", "024", "PÃ¡ez",
                "025", "PatÃ­a", "026", "Piamonte", "027", "PiendamÃ³",
                "028", "Puerto Tejada", "029", "Purace", "030", "Rosas",
                "031", "San SebastiÃ¡n", "032", "Santa Rosa", "033", "Santander de Quilichao",
                "034", "Silvia", "035", "Sotara", "036", "SuÃ¡rez",
                "037", "Sucre", "038", "TimbÃ­o", "039", "TimbiquÃ­",
                "040", "ToribÃ­o", "041", "TotorÃ³", "042", "Villa Rica"
            ]),
            "20": ("Cesar", [
                "001", "Valledupar", "002", "Aguachica", "003", "AgustÃ­n Codazzi",
                "004", "Astrea", "005", "Becerril", "006", "Bosconia",
                "007", "ChiriguanÃ¡", "008", "CurumanÃ­", "009", "El Copey",
                "010", "El Paso", "011", "Gamarra", "012", "GonzÃ¡lez",
                "013", "La Gloria", "014", "La Jagua de Ibirico", "015", "La Paz",
                "016", "Manaure", "017", "Pailitas", "018", "Pelaya",
                "019", "Pueblo Bello", "020", "RÃ­o de Oro", "021", "San Alberto",
                "022", "San Diego", "023", "San MartÃ­n", "024", "Tamalameque"
            ]),
            "23": ("CÃ³rdoba", [
                "001", "MonterÃ­a", "002", "Ayapel", "003", "Buenavista",
                "004", "Canalete", "005", "CeretÃ©", "006", "ChinÃº",
                "007", "CiÃ©naga de Oro", "008", "Cotorra", "009", "La Apartada",
                "010", "Los CÃ³rdobas", "011", "Momil", "012", "MontelÃ­bano",
                "013", "MoÃ±itos", "014", "Planeta Rica", "015", "Pueblo Nuevo",
                "016", "Puerto Escondido", "017", "Puerto Libertador", "018", "PurÃ­sima",
                "019", "SahagÃºn", "020", "San AndrÃ©s de Sotavento", "021", "San Antero",
                "022", "San Bernardo del Viento", "023", "San Carlos", "024", "San JosÃ© de Ure",
                "025", "San Pelayo", "026", "Santiago de TolÃº", "027", "Tierralta",
                "028", "TuchÃ­n", "029", "Valencia", "030", "Venecia"
            ]),
            "25": ("Cundinamarca", [
                "001", "Agua de Dios", "002", "AlbÃ¡n", "003", "Anapoima",
                "004", "Anolaima", "005", "Apulo", "006", "ArbelÃ¡ez",
                "007", "BeltrÃ¡n", "008", "Bituima", "009", "Bochalema",
                "010", "BogotÃ¡ D.C.", "011", "Cabrera", "012", "Cachipay",
                "013", "CajicÃ¡", "014", "CaparrapÃ­", "015", "CÃ¡queza",
                "016", "Carmen de Carupa", "017", "ChaguanÃ­", "018", "ChÃ­a",
                "019", "Chipaque", "020", "ChoachÃ­", "021", "ChocontÃ¡",
                "022", "Cogua", "023", "Cota", "024", "CucunubÃ¡",
                "025", "El Colegio", "026", "El PeÃ±Ã³n", "027", "El Rosal",
                "028", "FacatativÃ¡", "029", "FÃ³meque", "030", "Fosca",
                "031", "Funza", "032", "FÃºquene", "033", "FusagasugÃ¡",
                "034", "GachalÃ¡", "035", "GachancipÃ¡", "036", "GachetÃ¡",
                "037", "Gama", "038", "Girardot", "039", "Granada",
                "040", "GuachetÃ¡", "041", "Guaduas", "042", "Guasca",
                "043", "GuataquÃ­", "044", "Guatavita", "045", "Guayabal de SÃ­quima",
                "046", "Guayabetal", "047", "GutiÃ©rrez", "048", "JerusalÃ©n",
                "049", "JunÃ­n", "050", "La Calera", "051", "La Mesa",
                "052", "La Palma", "053", "La PeÃ±a", "054", "La Vega",
                "055", "Lenguazaque", "056", "Macheta", "057", "Madrid",
                "058", "Manta", "059", "Medina", "060", "Mosquera",
                "061", "NemocÃ³n", "062", "Nilo", "063", "Nimaima",
                "064", "Nocaima", "065", "Pacho", "066", "Paime",
                "067", "Pandi", "068", "Paratebueno", "069", "Pasca",
                "070", "Pesca", "071", "PulÃ­", "072", "Quebradanegra",
                "073", "Quetame", "074", "Quipile", "075", "Ricaurte",
                "076", "San Antonio del Tequendama", "077", "San Bernardo",
                "078", "San Cayetano", "079", "San Francisco", "080", "San Juan de RÃ­o Seco",
                "081", "Sasaima", "082", "SesquilÃ©", "083", "Silvania",
                "084", "Simijaca", "085", "Susa", "086", "Sutatausa",
                "087", "Tabio", "088", "Tausa", "089", "Tena",
                "090", "Tibacuy", "091", "Tibirita", "092", "Tocaima",
                "093", "TopaipÃ­", "094", "UbalÃ¡", "095", "Ubaque",
                "096", "Ubate", "097", "Une", "098", "Ãštica",
                "099", "Venecia", "100", "Vergara", "101", "VianÃ­",
                "102", "Villa GÃ³mez", "103", "Villa PinzÃ³n", "104", "Villeta",
                "105", "ViotÃ¡", "106", "YacopÃ­", "107", "ZipacÃ³n",
                "108", "ZipaquirÃ¡"
            ]),
            "27": ("ChocÃ³", [
                "001", "QuibdÃ³", "002", "AcandÃ­", "003", "Alto BaudÃ³",
                "004", "Atrato", "005", "BagadÃ³", "006", "BahÃ­a Solano",
                "007", "Bajo BaudÃ³", "008", "BojayÃ¡", "009", "CÃ©rtegui",
                "010", "Condoto", "011", "El Atrato", "012", "El Carmen del DariÃ©n",
                "013", "El Litoral del San Juan", "014", "Istmina", "015", "JuradÃ³",
                "016", "LlorÃ³", "017", "Medio Atrato", "018", "Medio BaudÃ³",
                "019", "Medio San Juan", "020", "NÃ³vita", "021", "NuquÃ­",
                "022", "PacÃ­fico", "023", "Pueblo Rico", "024", "RÃ­o IrÃ³",
                "025", "RÃ­o Quito", "026", "Riosucio", "027", "San JosÃ© del Palmar",
                "028", "SipÃ­", "029", "TadÃ³", "030", "UnguÃ­a"
            ]),
            "41": ("Huila", [
                "001", "Neiva", "002", "Acevedo", "003", "Agrado",
                "004", "Aipe", "005", "Algeciras", "006", "Altamira",
                "007", "Baraya", "008", "Campoalegre", "009", "Colombia",
                "010", "ElÃ­as", "011", "GarzÃ³n", "012", "Gigante",
                "013", "Guadalupe", "014", "Hobo", "015", "Iquira",
                "016", "Isnos", "017", "La Argentina", "018", "La Plata",
                "019", "NÃ¡taga", "020", "Oporapa", "021", "Paicol",
                "022", "Palermo", "023", "Palestina", "024", "Pital",
                "025", "Pitalito", "026", "Rivera", "027", "Saladoblanco",
                "028", "San AgustÃ­n", "029", "Santa MarÃ­a", "030", "Suaza",
                "031", "Tarqui", "032", "Tesalia", "033", "Tello",
                "034", "Teruel", "035", "TimanÃ¡", "036", "Villavieja",
                "037", "YaguarÃ¡"
            ]),
            "44": ("La Guajira", [
                "001", "Riohacha", "002", "Albania", "003", "Barrancas",
                "004", "Dibulla", "005", "DistracciÃ³n", "006", "El Molino",
                "007", "Fonseca", "008", "Hatonuevo", "009", "La Jagua del Pilar",
                "010", "Maicao", "011", "Manaure", "012", "San Juan del Cesar",
                "013", "Uribia", "014", "Urumita", "015", "Villanueva"
            ]),
            "47": ("Magdalena", [
                "001", "Santa Marta", "002", "Algarrobo", "003", "Aracataca",
                "004", "AriguanÃ­", "005", "Cerro San Antonio", "006", "Chivolo",
                "007", "CiÃ©naga", "008", "Concordia", "009", "El Banco",
                "010", "El PiÃ±Ã³n", "011", "El RetÃ©n", "012", "FundaciÃ³n",
                "013", "Guamal", "014", "Nueva Granada", "015", "Pedraza",
                "016", "Pivijay", "017", "PijiÃ±o del Carmen", "018", "Pivijay",
                "019", "Plato", "020", "Pueblo Viejo", "021", "Remolino",
                "022", "Sabanas de San Angel", "023", "Salamina", "024", "San SebastiÃ¡n de Buenavista",
                "025", "San ZenÃ³n", "026", "Santa Ana", "027", "Santa BÃ¡rbara de Pinto",
                "028", "Sitionuevo", "029", "Tenerife", "030", "ZapayÃ¡n",
                "031", "Zona Bananera"
            ]),
            "50": ("Meta", [
                "001", "Villavicencio", "002", "AcacÃ­as", "003", "Barranca de UpÃ­a",
                "004", "Cabuyaro", "005", "Castilla la Nueva", "006", "Cubarral",
                "007", "Cumaral", "008", "El Calvario", "009", "El Castillo",
                "010", "El Dorado", "011", "Fuente de Oro", "012", "Granada",
                "013", "Guamal", "014", "La Macarena", "015", "La Uribe",
                "016", "LejanÃ­as", "017", "MapiripÃ¡n", "018", "Mesetas",
                "019", "Puerto Concordia", "020", "Puerto GaitÃ¡n", "021", "Puerto Lleras",
                "022", "Puerto LÃ³pez", "023", "Puerto Rico", "024", "Restrepo",
                "025", "San Carlos de Guaroa", "026", "San Juan de Arama", "027", "San Juanito",
                "028", "San MartÃ­n", "029", "Vista Hermosa"
            ]),
            "52": ("NariÃ±o", [
                "001", "Pasto", "002", "AlbÃ¡n", "003", "Aldana",
                "004", "AncuyÃ¡", "005", "Arboleda", "006", "Barbacoas",
                "007", "BelÃ©n", "008", "Buesaco", "009", "ColÃ³n",
                "010", "ConsacÃ¡", "011", "Contadero", "012", "CÃ³rdoba",
                "013", "Cuaspud", "014", "Cumbal", "015", "Cumbitara",
                "016", "El Charco", "017", "El PeÃ±ol", "018", "El Rosario",
                "019", "El TablÃ³n de GÃ³mez", "020", "El Tambo", "021", "Francisco Pizarro",
                "022", "Funes", "023", "Guachucal", "024", "Guaitarilla",
                "025", "GualmatÃ¡n", "026", "Iles", "027", "ImuÃ©s",
                "028", "Ipiales", "029", "La Cruz", "030", "La Florida",
                "031", "La Llanada", "032", "La Tola", "033", "La UniÃ³n",
                "034", "Leiva", "035", "Linares", "036", "Los Andes",
                "037", "MagÃ¼Ã­", "038", "Mallama", "039", "Mosquera",
                "040", "NariÃ±o", "041", "Olaya Herrera", "042", "Ospina",
                "043", "Policarpa", "044", "PotosÃ­", "045", "Providencia",
                "046", "Puerres", "047", "Pupiales", "048", "Ricaurte",
                "049", "Roberto PayÃ¡n", "050", "Samaniego", "051", "San Bernardo",
                "052", "San Lorenzo", "053", "San Pablo", "054", "San Pedro de Cartago",
                "055", "Sandona", "056", "Santa BÃ¡rbara", "057", "Santacruz",
                "058", "Sapuyes", "059", "Tangua", "060", "Tumaco",
                "061", "TÃºquerres", "062", "Yacuanquer"
            ]),
            "54": ("Norte de Santander", [
                "001", "CÃºcuta", "002", "Abrego", "003", "Arboledas",
                "004", "Bochalema", "005", "Bucarasica", "006", "CÃ¡cota",
                "007", "CÃ¡chira", "008", "ChinÃ¡cota", "009", "ChitagÃ¡",
                "010", "ConvenciÃ³n", "011", "CÃºcuta", "012", "Cucutilla",
                "013", "Durania", "014", "El Carmen", "015", "El Tarra",
                "016", "El Zulia", "017", "Gramalote", "018", "HacarÃ­",
                "019", "HerrÃ¡n", "020", "La Esperanza", "021", "La Playa",
                "022", "Labateca", "023", "Los Patios", "024", "Lourdes",
                "025", "Mutiscua", "026", "OcaÃ±a", "027", "Pamplona",
                "028", "Pamplonita", "029", "Puerto Santander", "030", "Ragonvalia",
                "031", "Salazar", "032", "San Calixto", "033", "San Cayetano",
                "034", "Santiago", "035", "Santo Domingo", "036", "Sardinata",
                "037", "Teorama", "038", "TibÃº", "039", "Toledo",
                "040", "Villa Caro", "041", "Villa del Rosario", "042", "Villanueva"
            ]),
            "63": ("QuindÃ­o", [
                "001", "Armenia", "002", "Buenavista", "003", "CalarcÃ¡",
                "004", "Circasia", "005", "CÃ³rdoba", "006", "Filandia",
                "007", "GÃ©nova", "008", "La Tebaida", "009", "Montenegro",
                "010", "Pijao", "011", "Quimbaya", "012", "Salento"
            ]),
            "66": ("Risaralda", [
                "001", "Pereira", "002", "ApÃ­a", "003", "Balboa",
                "004", "BelÃ©n de UmbrÃ­a", "005", "Dosquebradas", "006", "GuÃ¡tica",
                "007", "La Celia", "008", "La Virginia", "009", "Marsella",
                "010", "MistratÃ³", "011", "Pueblo Rico", "012", "QuinchÃ­a",
                "013", "Santa Rosa de Cabal", "014", "Santuario"
            ]),
            "68": ("Santander", [
                "001", "Bucaramanga", "002", "Aguada", "003", "Albania",
                "004", "Aratoca", "005", "Barbosa", "006", "BolÃ­var",
                "007", "Burgos", "008", "Cabrera", "009", "California",
                "010", "Capitanejo", "011", "CarcasÃ­", "012", "CepitÃ¡",
                "013", "Cerrito", "014", "CharalÃ¡", "015", "Charta",
                "016", "Chima", "017", "ChipatÃ¡", "018", "Cimitarra",
                "019", "ConcepciÃ³n", "020", "Confines", "021", "ContrataciÃ³n",
                "022", "Coromoro", "023", "CuritÃ­", "024", "El Carmen de ChucurÃ­",
                "025", "El Guacamayo", "026", "El PeÃ±Ã³n", "027", "El PlayÃ³n",
                "028", "Encino", "029", "Enciso", "030", "FloriÃ¡n",
                "031", "Floridablanca", "032", "GalÃ¡n", "033", "GÃ¡mbita",
                "034", "GirÃ³n", "035", "Guaca", "036", "Guadalupe",
                "037", "GuapotÃ¡", "038", "GuavatÃ¡", "039", "GÃ¼epsa",
                "040", "Hato", "041", "JesÃºs MarÃ­a", "042", "JordÃ¡n",
                "043", "La Belleza", "044", "La Paz", "045", "LandÃ¡zuri",
                "046", "LebrÃ­ja", "047", "Los Santos", "048", "Macaravita",
                "049", "MÃ¡laga", "050", "Matanza", "051", "Mogotes",
                "052", "Molagavita", "053", "Ocamonte", "054", "Oiba",
                "055", "Onzaga", "056", "Palmar", "057", "Palmas del Socorro",
                "058", "PÃ¡ramo", "059", "Pinchote", "060", "Puente Nacional",
                "061", "Puerto Parra", "062", "Puerto Wilches", "063", "Rionegro",
                "064", "Sabana de Torres", "065", "San AndrÃ©s", "066", "San Benito",
                "067", "San Gil", "068", "San JoaquÃ­n", "069", "San JosÃ© de Miranda",
                "070", "San Miguel", "071", "San Vicente de ChucurÃ­", "072", "Santa BÃ¡rbara",
                "073", "Santa Helena del OpÃ³n", "074", "Simacota", "075", "Socorro",
                "076", "Suaita", "077", "Sucre", "078", "SuratÃ¡",
                "079", "Tona", "080", "Valle de San JosÃ©", "081", "VÃ©lez",
                "082", "Vetas", "083", "Villanueva", "084", "Zapatoca"
            ]),
            "70": ("Sucre", [
                "001", "Sincelejo", "002", "Buenavista", "003", "Caimito",
                "004", "ChalÃ¡n", "005", "Coloso", "006", "Corozal",
                "007", "CoveÃ±as", "008", "El Roble", "009", "Galeras",
                "010", "Guaranda", "011", "La UniÃ³n", "012", "Los Palmitos",
                "013", "Majagual", "014", "Morroa", "015", "Ovejas",
                "016", "Palmito", "017", "San Antonio de Palmito", "018", "San Benito Abad",
                "019", "San Juan de Betulia", "020", "San Luis de SincÃ©", "021", "San Marcos",
                "022", "San Onofre", "023", "San Pedro", "024", "SampuÃ©s",
                "025", "Santa Cruz de Lorica", "026", "Santiago de TolÃº", "027", "SincÃ©"
            ]),
            "73": ("Tolima", [
                "001", "IbaguÃ©", "002", "Alpujarra", "003", "Alvarado",
                "004", "Ambalema", "005", "AnzoÃ¡tegui", "006", "Armero",
                "007", "Ataco", "008", "Cajamarca", "009", "Carmen de ApicalÃ¡",
                "010", "Casabianca", "011", "Chaparral", "012", "Coello",
                "013", "Coyaima", "014", "Cunday", "015", "Dolores",
                "016", "Espinal", "017", "Falan", "018", "Flandes",
                "019", "Fresno", "020", "Guamo", "021", "Herveo",
                "022", "Honda", "023", "Icononzo", "024", "LÃ­bano",
                "025", "Mariquita", "026", "Melgar", "027", "Murillo",
                "028", "Natagaima", "029", "Ortega", "030", "Palocabildo",
                "031", "Piedras", "032", "Planadas", "033", "Prado",
                "034", "PurificaciÃ³n", "035", "Rioblanco", "036", "Roncesvalles",
                "037", "Rovira", "038", "SaldaÃ±a", "039", "San Antonio",
                "040", "San LuÃ­s", "041", "Santa Isabel", "042", "SuÃ¡rez",
                "043", "Valle de San Juan", "044", "Venadillo", "045", "Villahermosa",
                "046", "Villarrica"
            ]),
            "76": ("Valle del Cauca", [
                "001", "Cali", "002", "AlcalÃ¡", "003", "AndalucÃ­a",
                "004", "Ansermanuevo", "005", "Argelia", "006", "BolÃ­var",
                "007", "Buenaventura", "008", "Buga", "009", "Bugalagrande",
                "010", "Caicedonia", "011", "Calima", "012", "Candelaria",
                "013", "Cartago", "014", "Dagua", "015", "El Ãguila",
                "016", "El Cairo", "017", "El Cerrito", "018", "El Dovio",
                "019", "Florida", "020", "Ginebra", "021", "GuacarÃ­",
                "022", "Guadalajara de Buga", "023", "JamundÃ­", "024", "La Cumbre",
                "025", "La UniÃ³n", "026", "La Victoria", "027", "Obando",
                "028", "Palmira", "029", "Pradera", "030", "Restrepo",
                "031", "RiofrÃ­o", "032", "Roldanillo", "033", "San Pedro",
                "034", "Sevilla", "035", "Toro", "036", "Trujillo",
                "037", "TuluÃ¡", "038", "Ulloa", "039", "Versalles",
                "040", "Vijes", "041", "Yotoco", "042", "Yumbo",
                "043", "Zarzal"
            ]),
            "81": ("Arauca", [
                "001", "Arauca", "002", "Arauquita", "003", "Cravo Norte",
                "004", "Fortul", "005", "Puerto RondÃ³n", "006", "Saravena",
                "007", "Tame"
            ]),
            "85": ("Casanare", [
                "001", "Yopal", "002", "Aguazul", "003", "ChÃ¡meza",
                "004", "Hato Corozal", "005", "La Salina", "006", "ManÃ­",
                "007", "Monterrey", "008", "NunchÃ­a", "009", "OrocuÃ©",
                "010", "Paz de Ariporo", "011", "Pore", "012", "Recetor",
                "013", "Sabanalarga", "014", "SÃ¡cama", "015", "San LuÃ­s de Palenque",
                "016", "TÃ¡mara", "017", "Tauramena", "018", "Trinidad",
                "019", "Villanueva"
            ]),
            "86": ("Putumayo", [
                "001", "Mocoa", "002", "ColÃ³n", "003", "LeguÃ­zamo",
                "004", "Orito", "005", "Puerto AsÃ­s", "006", "Puerto Caicedo",
                "007", "Puerto GuzmÃ¡n", "008", "San Francisco", "009", "San Miguel",
                "010", "Santiago", "011", "Sibundoy", "012", "Valle del Guamuez",
                "013", "VillagarzÃ³n"
            ]),
            "88": ("ArchipiÃ©lago de San AndrÃ©s", [
                "001", "San AndrÃ©s", "002", "Providencia"
            ]),
            "91": ("Amazonas", [
                "001", "Leticia", "002", "El Encanto", "003", "La Chorrera",
                "004", "La Pedrera", "005", "La Victoria", "006", "Miriti - ParanÃ¡",
                "007", "Puerto Arica", "008", "Puerto NariÃ±o", "009", "Puerto Santander",
                "010", "TarapacÃ¡"
            ]),
            "94": ("GuainÃ­a", [
                "001", "InÃ­rida", "002", "Barranco Minas", "003", "Mapiripana",
                "004", "San Felipe", "005", "Puerto Colombia", "006", "La Guadalupe",
                "007", "Cacahual", "008", "Pana Pana", "009", "Morichal"
            ]),
            "95": ("Guaviare", [
                "001", "San JosÃ© del Guaviare", "002", "Calamar", "003", "El Retorno",
                "004", "Miraflores"
            ]),
            "97": ("VaupÃ©s", [
                "001", "MitÃº", "002", "CarurÃº", "003", "Pacoa",
                "004", "Taraira", "005", "YavaratÃ©"
            ]),
            "99": ("Vichada", [
                "001", "Puerto CarreÃ±o", "002", "La Primavera", "003", "Santa RosalÃ­a",
                "004", "Cumaribo"
            ])
        }

        total_dept = 0
        total_mun = 0
        
        for codigo, (nombre_dept, municipios) in data.items():
            # Crear o obtener el departamento
            departamento, created = Departamento.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre_dept}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'âœ“ Departamento: {nombre_dept}'))
                total_dept += 1
            
            # Crear municipios del departamento (cÃ³digo y nombre estÃ¡n intercalados)
            i = 0
            while i < len(municipios):
                codigo_mun = municipios[i]
                nombre_mun = municipios[i + 1] if i + 1 < len(municipios) else ""
                
                if nombre_mun:  # Solo si hay nombre disponible
                    municipio, mun_created = Municipio.objects.get_or_create(
                        departamento=departamento,
                        codigo=codigo_mun,
                        defaults={'nombre': nombre_mun}
                    )
                    
                    if mun_created:
                        total_mun += 1
                
                i += 2  # Avanzar dos posiciones (cÃ³digo y nombre)

        self.stdout.write(self.style.SUCCESS(f'\nâœ“ Seed completado: {total_dept} departamentos, {total_mun} municipios creados.'))


