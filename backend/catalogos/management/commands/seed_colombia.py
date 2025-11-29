from django.core.management.base import BaseCommand
from catalogos.models import Departamento, Municipio

# Constants for frequently duplicated municipality names
MUNICIPALITY_LA_UNION = "La Unión"
MUNICIPALITY_NARINO = "Nariño"
MUNICIPALITY_SAN_FRANCISCO = "San Francisco"
MUNICIPALITY_SAN_ANDRES = "San Andrés"
MUNICIPALITY_SAN_PEDRO = "San Pedro"
MUNICIPALITY_SANTA_BARBARA = "Santa Bárbara"
MUNICIPALITY_BOGOTA_DC = "Bogotá D.C."
MUNICIPALITY_BOLIVAR = "Bolívar"
MUNICIPALITY_CORDOBA = "Córdoba"
MUNICIPALITY_EL_PENON = "El Peñón"
MUNICIPALITY_LA_VICTORIA = "La Victoria"


def _normalize_text(value: str) -> str:
    """
    Corrige textos que quedaron con codificación UTF-8 interpretada como Latin-1.
    """
    if not isinstance(value, str):
        return value
    if 'Ã' in value or 'Â' in value or 'ð' in value:
        try:
            return value.encode('latin-1').decode('utf-8')
        except UnicodeEncodeError:
            return value
    return value


class Command(BaseCommand):
    help = "Cargar todos los departamentos y municipios de Colombia"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de departamentos y municipios de Colombia...'))

        # Datos completos de Colombia (32 departamentos + Bogotá D.C.)
        data = {
            "05": ("Antioquia", [
                "001", "Medellín", "002", "Bello", "003", "Itagüí", "004", "Envigado",
                "005", "Rionegro", "008", "La Ceja", "009", "Marinilla", "011", "El Retiro",
                "013", "Guarne", "014", "Guatapé", "015", "Concepción", "016", "Alejandría",
                "017", "El Carmen de Viboral", "019", "Granada", "021", "Santuario",
                "023", "Porfirio Barba Jacob", "024", "Cisneros", "025", "Aguadas",
                "026", "Anserma", "027", "Aranzazu", "028", "Belmira", "029", "Betania",
                "031", "Betulia", "033", "Briceño", "034", "Buriticá", "035", "Caicedo",
                "036", "Caldas", "037", "Campamento", "038", "Cañasgordas", "039", "Caracolí",
                "040", "Caramanta", "041", "Carepa", "043", "Carolina", "044", "Donmatías",
                "045", "Ebéjico", "046", "El Bagre", "048", "Entrerríos", "049", "Epitacio",
                "051", "Fredonia", "052", "Frontino", "053", "Giraldo", "054", "Girardota",
                "055", "Gómez Plata", "056", "Guadalupe", "057", "Heliconia", "059", "Hispania",
                "060", "Ituango", "062", "Jericó", "063", "La Estrella", "064", "La Pintada",
                "065", MUNICIPALITY_LA_UNION, "066", "Liborina", "067", "Maceo", "069", "Montebello",
                "070", "Mutatá", "071", "Nariño", "072", "Nechí", "073", "Necoclí",
                "074", "Olaya", "075", "Peque", "076", "Pueblorrico", "077", "Puerto Berrío",
                "078", "Puerto Nare", "079", "Puerto Triunfo", "080", "Remedios", "081", "Retiro",
                "082", "Rionegro", "084", "Sabanalarga", "085", "Sabaneta", "086", "Salgar",
                "087", MUNICIPALITY_SAN_ANDRES, "088", "San Carlos", "089", MUNICIPALITY_SAN_FRANCISCO, "090", "San Jerónimo",
                "091", "San José de la Montaña", "092", "San Juan de Urabá", "093", "San Luís",
                "094", MUNICIPALITY_SAN_PEDRO, "095", "San Pedro de Urabá", "096", "San Rafael", "097", "San Roque",
                "098", "San Vicente", "099", MUNICIPALITY_SANTA_BARBARA, "100", "Santa Fé de Antioquia",
                "101", "Santa Rosa de Osos", "102", "Santo Domingo", "103", "Santuario",
                "104", "Segovia", "105", "Sonsón", "106", "Sopetrán", "107", "Támesis",
                "108", "Tarazá", "109", "Tarso", "110", "Titiribí", "111", "Toledo",
                "112", "Turbo", "113", "Uramita", "114", "Urrao", "115", "Valdivia",
                "116", "Valparaíso", "117", "Vegachí", "118", "Venecia", "119", "Vigía del Fuerte",
                "121", "Yalí", "122", "Yarumal", "123", "Yolombó", "124", "Yondó",
                "125", "Zaragoza"
            ]),
            "08": ("Atlántico", [
                "001", "Barranquilla", "002", "Baranoa", "003", "Campo de la Cruz",
                "004", "Candelaria", "005", "Galapa", "006", "Juan de Acosta",
                "007", "Luruaco", "008", "Malambo", "009", "Manatí",
                "010", "Palmar de Varela", "011", "Piojó", "012", "Polonuevo",
                "013", "Ponedera", "014", "Puerto Colombia", "015", "Repelón",
                "016", "Sabanagrande", "017", "Sabanalarga", "018", "Santa Lucía",
                "019", "Santo Tomás", "020", "Soledad", "021", "Suan",
                "022", "Tubará", "023", "Usiacurí"
            ]),
            "11": (MUNICIPALITY_BOGOTA_DC, [
                "001", MUNICIPALITY_BOGOTA_DC
            ]),
            "13": (MUNICIPALITY_BOLIVAR, [
                "001", "Cartagena", "002", "Achí", "003", "Altos del Rosario",
                "004", "Arenal", "005", "Arjona", "006", "Arroyohondo",
                "007", "Barranco de Loba", "008", "Calamar", "009", "Cantagallo",
                "010", "Cicuco", "011", MUNICIPALITY_CORDOBA, "012", "Clemencia",
                "013", "El Carmen de Bolívar", "014", "El Guamo", "015", MUNICIPALITY_EL_PENON,
                "016", "Hatonuevo", "017", "Magangué", "018", "Mahates",
                "019", "Margarita", "020", "María la Baja", "021", "Mompós",
                "022", "Montecristo", "023", "Morales", "024", "Norosí",
                "025", "Pinillos", "026", "Regidor", "027", "Río Viejo",
                "028", "San Cristóbal", "029", "San Estanislao", "030", "San Fernando",
                "031", "San Jacinto", "032", "San Jacinto del Cauca", "033", "San Juan Nepomuceno",
                "034", "San Martín de Loba", "035", "San Pablo", "036", "Santa Catalina",
                "037", "Santa Rosa", "038", "Santa Rosa del Sur", "039", "Simití",
                "040", "Soplaviento", "041", "Talaigua Nuevo", "042", "Tiquisio",
                "043", "Turbaco", "044", "Turbaná", "045", "Villanueva",
                "046", "Zambrano"
            ]),
            "15": ("Boyacá", [
                "001", "Tunja", "002", "Almeida", "003", "Aquitania",
                "004", "Arcabuco", "005", "Belén", "006", "Berbeo",
                "007", "Betéitiva", "008", "Boavita", "009", "Boyacá",
                "010", "Briceño", "011", "Buenavista", "012", "Busbanzá",
                "013", "Caldas", "014", "Campohermoso", "015", "Cerinza",
                "016", "Chinavita", "017", "Chiquinquirá", "018", "Chiscas",
                "019", "Chita", "020", "Chitaraque", "021", "Chivatá",
                "022", "Ciénega", "023", "Cómbita", "024", "Coper",
                "025", "Corrales", "026", "Covarachía", "027", "Cubará",
                "028", "Cucaita", "029", "Cuítiva", "030", "Duitama",
                "031", "El Cocuy", "032", "El Espino", "033", "Firavitoba",
                "034", "Floresta", "035", "Gachantivá", "036", "Gámeza",
                "037", "Garagoa", "038", "Guacamayas", "039", "Guateque",
                "040", "Guayatá", "041", "Güicán", "042", "Iza",
                "043", "Jenesano", "044", "Jericó", "045", "Labranzagrande",
                "046", "La Capilla", "047", MUNICIPALITY_LA_VICTORIA, "048", "La Uvita",
                "049", "Villa de Leyva", "050", "Macanal", "051", "Maripí",
                "052", "Miraflores", "053", "Mongua", "054", "Monguí",
                "055", "Moniquirá", "056", "Motavita", "057", "Muzo",
                "058", "Nobsa", "059", "Nuevo Colón", "060", "Oicatá",
                "061", "Otanche", "062", "Pachavita", "063", "Páez",
                "064", "Paipa", "065", "Pajarito", "066", "Panqueba",
                "067", "Pauna", "068", "Paya", "069", "Paz de Río",
                "070", "Pesca", "071", "Pisba", "072", "Puerto Boyacá",
                "073", "Quípama", "074", "Ramiriquí", "075", "Ráquira",
                "076", "Rondón", "077", "Saboyá", "078", "Sáchica",
                "079", "Samacá", "080", "San Eduardo", "081", "San José de Pare",
                "082", "San Luís de Gaceno", "083", "San Mateo", "084", "San Miguel de Sema",
                "085", "San Pablo de Borbur", "086", "Santana", "087", "Santa María",
                "088", "Santa Rosa de Viterbo", "089", "Santa Sofía", "090", "Sativanorte",
                "091", "Sativasur", "092", "Siachoque", "093", "Soatá",
                "094", "Socha", "095", "Socotá", "096", "Sogamoso",
                "097", "Somondoco", "098", "Sora", "099", "Soracá",
                "100", "Sotaquirá", "101", "Susacón", "102", "Sutamarchán",
                "103", "Sutatenza", "104", "Tasco", "105", "Tenza",
                "106", "Tibaná", "107", "Tibasosa", "108", "Tinjacá",
                "109", "Tipacoque", "110", "Toca", "111", "Togüí",
                "112", "Tópaga", "113", "Tota", "114", "Tununguá",
                "115", "Turmequé", "116", "Tuta", "117", "Tutazá",
                "118", "mbita", "119", "Ventaquemada", "120", "Villa de San Diego de Ubaté",
                "121", "Viracachá", "122", "Zetaquira"
            ]),
            "17": ("Caldas", [
                "001", "Manizales", "002", "Aguadas", "003", "Anserma",
                "004", "Aranzazu", "005", "Belalcázar", "006", "Chinchiná",
                "007", "Filadelfia", "008", "La Dorada", "009", "La Merced",
                "010", "Manzanares", "011", "Marmato", "012", "Marquetalia",
                "013", "Marulanda", "014", "Neira", "015", "Norcasia",
                "016", "Pácora", "017", "Palestina", "018", "Pensilvania",
                "019", "Riosucio", "020", "Risaralda", "021", "Salamina",
                "022", "Samaná", "023", "San José", "024", "Supía",
                "025", "Victoria", "026", "Villamaría", "027", "Viterbo"
            ]),
            "18": ("Caquetá", [
                "001", "Florencia", "002", "Albania", "003", "Belén de los Andaquies",
                "004", "Cartagena del Chairá", "005", "Curillo", "006", "El Doncello",
                "007", "El Paujil", "008", "La Montañita", "009", "Milán",
                "010", "Morelia", "011", "Puerto Rico", "012", "San José del Fragua",
                "013", "San Vicente del Caguán", "014", "Solano", "015", "Solita",
                "016", "Valparaíso"
            ]),
            "19": ("Cauca", [
                "001", "Popayán", "002", "Almaguer", "003", "Argelia",
                "004", "Balboa", "005", MUNICIPALITY_BOLIVAR, "006", "Buenos Aires",
                "007", "Cajibío", "008", "Caldono", "009", "Caloto",
                "010", "Corinto", "011", "El Tambo", "012", "Florencia",
                "013", "Guachené", "014", "Guapi", "015", "Inzá",
                "016", "Jambaló", "017", "La Sierra", "018", "La Vega",
                "019", "López", "020", "Mercaderes", "021", "Miranda",
                "022", "Morales", "023", "Padilla", "024", "Páez",
                "025", "Patía", "026", "Piamonte", "027", "Piendamó",
                "028", "Puerto Tejada", "029", "Purace", "030", "Rosas",
                "031", "San Sebastián", "032", "Santa Rosa", "033", "Santander de Quilichao",
                "034", "Silvia", "035", "Sotara", "036", "Suárez",
                "037", "Sucre", "038", "Timbío", "039", "Timbiquí",
                "040", "Toribío", "041", "Totoró", "042", "Villa Rica"
            ]),
            "20": ("Cesar", [
                "001", "Valledupar", "002", "Aguachica", "003", "Agustín Codazzi",
                "004", "Astrea", "005", "Becerril", "006", "Bosconia",
                "007", "Chiriguaná", "008", "Curumaní", "009", "El Copey",
                "010", "El Paso", "011", "Gamarra", "012", "González",
                "013", "La Gloria", "014", "La Jagua de Ibirico", "015", "La Paz",
                "016", "Manaure", "017", "Pailitas", "018", "Pelaya",
                "019", "Pueblo Bello", "020", "Río de Oro", "021", "San Alberto",
                "022", "San Diego", "023", "San Martín", "024", "Tamalameque"
            ]),
            "23": (MUNICIPALITY_CORDOBA, [
                "001", "Montería", "002", "Ayapel", "003", "Buenavista",
                "004", "Canalete", "005", "Cereté", "006", "Chinú",
                "007", "Ciénaga de Oro", "008", "Cotorra", "009", "La Apartada",
                "010", "Los Córdobas", "011", "Momil", "012", "Montelíbano",
                "013", "Moñitos", "014", "Planeta Rica", "015", "Pueblo Nuevo",
                "016", "Puerto Escondido", "017", "Puerto Libertador", "018", "Purísima",
                "019", "Sahagún", "020", "San Andrés de Sotavento", "021", "San Antero",
                "022", "San Bernardo del Viento", "023", "San Carlos", "024", "San José de Ure",
                "025", "San Pelayo", "026", "Santiago de Tolú", "027", "Tierralta",
                "028", "Tuchín", "029", "Valencia", "030", "Venecia"
            ]),
            "25": ("Cundinamarca", [
                "001", "Agua de Dios", "002", "Albán", "003", "Anapoima",
                "004", "Anolaima", "005", "Apulo", "006", "Arbeláez",
                "007", "Beltrán", "008", "Bituima", "009", "Bochalema",
                "010", MUNICIPALITY_BOGOTA_DC, "011", "Cabrera", "012", "Cachipay",
                "013", "Cajicá", "014", "Caparrapí", "015", "Cáqueza",
                "016", "Carmen de Carupa", "017", "Chaguaní", "018", "Chía",
                "019", "Chipaque", "020", "Choachí", "021", "Chocontá",
                "022", "Cogua", "023", "Cota", "024", "Cucunubá",
                "025", "El Colegio", "026", MUNICIPALITY_EL_PENON, "027", "El Rosal",
                "028", "Facatativá", "029", "Fómeque", "030", "Fosca",
                "031", "Funza", "032", "Fúquene", "033", "Fusagasugá",
                "034", "Gachalá", "035", "Gachancipá", "036", "Gachetá",
                "037", "Gama", "038", "Girardot", "039", "Granada",
                "040", "Guachetá", "041", "Guaduas", "042", "Guasca",
                "043", "Guataquí", "044", "Guatavita", "045", "Guayabal de Síquima",
                "046", "Guayabetal", "047", "Gutiérrez", "048", "Jerusalén",
                "049", "Junín", "050", "La Calera", "051", "La Mesa",
                "052", "La Palma", "053", "La Peña", "054", "La Vega",
                "055", "Lenguazaque", "056", "Macheta", "057", "Madrid",
                "058", "Manta", "059", "Medina", "060", "Mosquera",
                "061", "Nemocón", "062", "Nilo", "063", "Nimaima",
                "064", "Nocaima", "065", "Pacho", "066", "Paime",
                "067", "Pandi", "068", "Paratebueno", "069", "Pasca",
                "070", "Pesca", "071", "Pulí", "072", "Quebradanegra",
                "073", "Quetame", "074", "Quipile", "075", "Ricaurte",
                "076", "San Antonio del Tequendama", "077", "San Bernardo",
                "078", "San Cayetano", "079", MUNICIPALITY_SAN_FRANCISCO, "080", "San Juan de Río Seco",
                "081", "Sasaima", "082", "Sesquilé", "083", "Silvania",
                "084", "Simijaca", "085", "Susa", "086", "Sutatausa",
                "087", "Tabio", "088", "Tausa", "089", "Tena",
                "090", "Tibacuy", "091", "Tibirita", "092", "Tocaima",
                "093", "Topaipí", "094", "Ubalá", "095", "Ubaque",
                "096", "Ubate", "097", "Une", "098", "tica",
                "099", "Venecia", "100", "Vergara", "101", "Vianí",
                "102", "Villa Gómez", "103", "Villa Pinzón", "104", "Villeta",
                "105", "Viotá", "106", "Yacopí", "107", "Zipacón",
                "108", "Zipaquirá"
            ]),
            "27": ("Chocó", [
                "001", "Quibdó", "002", "Acandí", "003", "Alto Baudó",
                "004", "Atrato", "005", "Bagadó", "006", "Bahía Solano",
                "007", "Bajo Baudó", "008", "Bojayá", "009", "Cértegui",
                "010", "Condoto", "011", "El Atrato", "012", "El Carmen del Darién",
                "013", "El Litoral del San Juan", "014", "Istmina", "015", "Juradó",
                "016", "Lloró", "017", "Medio Atrato", "018", "Medio Baudó",
                "019", "Medio San Juan", "020", "Nóvita", "021", "Nuquí",
                "022", "Pacífico", "023", "Pueblo Rico", "024", "Río Iró",
                "025", "Río Quito", "026", "Riosucio", "027", "San José del Palmar",
                "028", "Sipí", "029", "Tadó", "030", "Unguía"
            ]),
            "41": ("Huila", [
                "001", "Neiva", "002", "Acevedo", "003", "Agrado",
                "004", "Aipe", "005", "Algeciras", "006", "Altamira",
                "007", "Baraya", "008", "Campoalegre", "009", "Colombia",
                "010", "Elías", "011", "Garzón", "012", "Gigante",
                "013", "Guadalupe", "014", "Hobo", "015", "Iquira",
                "016", "Isnos", "017", "La Argentina", "018", "La Plata",
                "019", "Nátaga", "020", "Oporapa", "021", "Paicol",
                "022", "Palermo", "023", "Palestina", "024", "Pital",
                "025", "Pitalito", "026", "Rivera", "027", "Saladoblanco",
                "028", "San Agustín", "029", "Santa María", "030", "Suaza",
                "031", "Tarqui", "032", "Tesalia", "033", "Tello",
                "034", "Teruel", "035", "Timaná", "036", "Villavieja",
                "037", "Yaguará"
            ]),
            "44": ("La Guajira", [
                "001", "Riohacha", "002", "Albania", "003", "Barrancas",
                "004", "Dibulla", "005", "Distracción", "006", "El Molino",
                "007", "Fonseca", "008", "Hatonuevo", "009", "La Jagua del Pilar",
                "010", "Maicao", "011", "Manaure", "012", "San Juan del Cesar",
                "013", "Uribia", "014", "Urumita", "015", "Villanueva"
            ]),
            "47": ("Magdalena", [
                "001", "Santa Marta", "002", "Algarrobo", "003", "Aracataca",
                "004", "Ariguaní", "005", "Cerro San Antonio", "006", "Chivolo",
                "007", "Ciénaga", "008", "Concordia", "009", "El Banco",
                "010", "El Piñón", "011", "El Retén", "012", "Fundación",
                "013", "Guamal", "014", "Nueva Granada", "015", "Pedraza",
                "016", "Pivijay", "017", "Pijiño del Carmen", "018", "Pivijay",
                "019", "Plato", "020", "Pueblo Viejo", "021", "Remolino",
                "022", "Sabanas de San Angel", "023", "Salamina", "024", "San Sebastián de Buenavista",
                "025", "San Zenón", "026", "Santa Ana", "027", "Santa Bárbara de Pinto",
                "028", "Sitionuevo", "029", "Tenerife", "030", "Zapayán",
                "031", "Zona Bananera"
            ]),
            "50": ("Meta", [
                "001", "Villavicencio", "002", "Acacías", "003", "Barranca de Upía",
                "004", "Cabuyaro", "005", "Castilla la Nueva", "006", "Cubarral",
                "007", "Cumaral", "008", "El Calvario", "009", "El Castillo",
                "010", "El Dorado", "011", "Fuente de Oro", "012", "Granada",
                "013", "Guamal", "014", "La Macarena", "015", "La Uribe",
                "016", "Lejanías", "017", "Mapiripán", "018", "Mesetas",
                "019", "Puerto Concordia", "020", "Puerto Gaitán", "021", "Puerto Lleras",
                "022", "Puerto López", "023", "Puerto Rico", "024", "Restrepo",
                "025", "San Carlos de Guaroa", "026", "San Juan de Arama", "027", "San Juanito",
                "028", "San Martín", "029", "Vista Hermosa"
            ]),
            "52": (MUNICIPALITY_NARINO, [
                "001", "Pasto", "002", "Albán", "003", "Aldana",
                "004", "Ancuyá", "005", "Arboleda", "006", "Barbacoas",
                "007", "Belén", "008", "Buesaco", "009", "Colón",
                "010", "Consacá", "011", "Contadero", "012", MUNICIPALITY_CORDOBA,
                "013", "Cuaspud", "014", "Cumbal", "015", "Cumbitara",
                "016", "El Charco", "017", "El Peñol", "018", "El Rosario",
                "019", "El Tablón de Gómez", "020", "El Tambo", "021", "Francisco Pizarro",
                "022", "Funes", "023", "Guachucal", "024", "Guaitarilla",
                "025", "Gualmatán", "026", "Iles", "027", "Imués",
                "028", "Ipiales", "029", "La Cruz", "030", "La Florida",
                "031", "La Llanada", "032", "La Tola", "033", MUNICIPALITY_LA_UNION,
                "034", "Leiva", "035", "Linares", "036", "Los Andes",
                "037", "Magüí", "038", "Mallama", "039", "Mosquera",
                "040", MUNICIPALITY_NARINO, "041", "Olaya Herrera", "042", "Ospina",
                "043", "Policarpa", "044", "Potosí", "045", "Providencia",
                "046", "Puerres", "047", "Pupiales", "048", "Ricaurte",
                "049", "Roberto Payán", "050", "Samaniego", "051", "San Bernardo",
                "052", "San Lorenzo", "053", "San Pablo", "054", "San Pedro de Cartago",
                "055", "Sandona", "056", MUNICIPALITY_SANTA_BARBARA, "057", "Santacruz",
                "058", "Sapuyes", "059", "Tangua", "060", "Tumaco",
                "061", "Túquerres", "062", "Yacuanquer"
            ]),
            "54": ("Norte de Santander", [
                "001", "Cúcuta", "002", "Abrego", "003", "Arboledas",
                "004", "Bochalema", "005", "Bucarasica", "006", "Cácota",
                "007", "Cáchira", "008", "Chinácota", "009", "Chitagá",
                "010", "Convención", "011", "Cúcuta", "012", "Cucutilla",
                "013", "Durania", "014", "El Carmen", "015", "El Tarra",
                "016", "El Zulia", "017", "Gramalote", "018", "Hacarí",
                "019", "Herrán", "020", "La Esperanza", "021", "La Playa",
                "022", "Labateca", "023", "Los Patios", "024", "Lourdes",
                "025", "Mutiscua", "026", "Ocaña", "027", "Pamplona",
                "028", "Pamplonita", "029", "Puerto Santander", "030", "Ragonvalia",
                "031", "Salazar", "032", "San Calixto", "033", "San Cayetano",
                "034", "Santiago", "035", "Santo Domingo", "036", "Sardinata",
                "037", "Teorama", "038", "Tibú", "039", "Toledo",
                "040", "Villa Caro", "041", "Villa del Rosario", "042", "Villanueva"
            ]),
            "63": ("Quindío", [
                "001", "Armenia", "002", "Buenavista", "003", "Calarcá",
                "004", "Circasia", "005", MUNICIPALITY_CORDOBA, "006", "Filandia",
                "007", "Génova", "008", "La Tebaida", "009", "Montenegro",
                "010", "Pijao", "011", "Quimbaya", "012", "Salento"
            ]),
            "66": ("Risaralda", [
                "001", "Pereira", "002", "Apía", "003", "Balboa",
                "004", "Belén de Umbría", "005", "Dosquebradas", "006", "Guática",
                "007", "La Celia", "008", "La Virginia", "009", "Marsella",
                "010", "Mistrató", "011", "Pueblo Rico", "012", "Quinchía",
                "013", "Santa Rosa de Cabal", "014", "Santuario"
            ]),
            "68": ("Santander", [
                "001", "Bucaramanga", "002", "Aguada", "003", "Albania",
                "004", "Aratoca", "005", "Barbosa", "006", MUNICIPALITY_BOLIVAR,
                "007", "Burgos", "008", "Cabrera", "009", "California",
                "010", "Capitanejo", "011", "Carcasí", "012", "Cepitá",
                "013", "Cerrito", "014", "Charalá", "015", "Charta",
                "016", "Chima", "017", "Chipatá", "018", "Cimitarra",
                "019", "Concepción", "020", "Confines", "021", "Contratación",
                "022", "Coromoro", "023", "Curití", "024", "El Carmen de Chucurí",
                "025", "El Guacamayo", "026", MUNICIPALITY_EL_PENON, "027", "El Playón",
                "028", "Encino", "029", "Enciso", "030", "Florián",
                "031", "Floridablanca", "032", "Galán", "033", "Gámbita",
                "034", "Girón", "035", "Guaca", "036", "Guadalupe",
                "037", "Guapotá", "038", "Guavatá", "039", "Güepsa",
                "040", "Hato", "041", "Jesús María", "042", "Jordán",
                "043", "La Belleza", "044", "La Paz", "045", "Landázuri",
                "046", "Lebríja", "047", "Los Santos", "048", "Macaravita",
                "049", "Málaga", "050", "Matanza", "051", "Mogotes",
                "052", "Molagavita", "053", "Ocamonte", "054", "Oiba",
                "055", "Onzaga", "056", "Palmar", "057", "Palmas del Socorro",
                "058", "Páramo", "059", "Pinchote", "060", "Puente Nacional",
                "061", "Puerto Parra", "062", "Puerto Wilches", "063", "Rionegro",
                "064", "Sabana de Torres", "065", "San Andrés", "066", "San Benito",
                "067", "San Gil", "068", "San Joaquín", "069", "San José de Miranda",
                "070", "San Miguel", "071", "San Vicente de Chucurí", "072", MUNICIPALITY_SANTA_BARBARA,
                "073", "Santa Helena del Opón", "074", "Simacota", "075", "Socorro",
                "076", "Suaita", "077", "Sucre", "078", "Suratá",
                "079", "Tona", "080", "Valle de San José", "081", "Vélez",
                "082", "Vetas", "083", "Villanueva", "084", "Zapatoca"
            ]),
            "70": ("Sucre", [
                "001", "Sincelejo", "002", "Buenavista", "003", "Caimito",
                "004", "Chalán", "005", "Coloso", "006", "Corozal",
                "007", "Coveñas", "008", "El Roble", "009", "Galeras",
                "010", "Guaranda", "011", MUNICIPALITY_LA_UNION, "012", "Los Palmitos",
                "013", "Majagual", "014", "Morroa", "015", "Ovejas",
                "016", "Palmito", "017", "San Antonio de Palmito", "018", "San Benito Abad",
                "019", "San Juan de Betulia", "020", "San Luis de Sincé", "021", "San Marcos",
                "022", "San Onofre", "023", MUNICIPALITY_SAN_PEDRO, "024", "Sampués",
                "025", "Santa Cruz de Lorica", "026", "Santiago de Tolú", "027", "Sincé"
            ]),
            "73": ("Tolima", [
                "001", "Ibagué", "002", "Alpujarra", "003", "Alvarado",
                "004", "Ambalema", "005", "Anzoátegui", "006", "Armero",
                "007", "Ataco", "008", "Cajamarca", "009", "Carmen de Apicalá",
                "010", "Casabianca", "011", "Chaparral", "012", "Coello",
                "013", "Coyaima", "014", "Cunday", "015", "Dolores",
                "016", "Espinal", "017", "Falan", "018", "Flandes",
                "019", "Fresno", "020", "Guamo", "021", "Herveo",
                "022", "Honda", "023", "Icononzo", "024", "Líbano",
                "025", "Mariquita", "026", "Melgar", "027", "Murillo",
                "028", "Natagaima", "029", "Ortega", "030", "Palocabildo",
                "031", "Piedras", "032", "Planadas", "033", "Prado",
                "034", "Purificación", "035", "Rioblanco", "036", "Roncesvalles",
                "037", "Rovira", "038", "Saldaña", "039", "San Antonio",
                "040", "San Luís", "041", "Santa Isabel", "042", "Suárez",
                "043", "Valle de San Juan", "044", "Venadillo", "045", "Villahermosa",
                "046", "Villarrica"
            ]),
            "76": ("Valle del Cauca", [
                "001", "Cali", "002", "Alcalá", "003", "Andalucía",
                "004", "Ansermanuevo", "005", "Argelia", "006", MUNICIPALITY_BOLIVAR,
                "007", "Buenaventura", "008", "Buga", "009", "Bugalagrande",
                "010", "Caicedonia", "011", "Calima", "012", "Candelaria",
                "013", "Cartago", "014", "Dagua", "015", "El Águila",
                "016", "El Cairo", "017", "El Cerrito", "018", "El Dovio",
                "019", "Florida", "020", "Ginebra", "021", "Guacarí",
                "022", "Guadalajara de Buga", "023", "Jamundí", "024", "La Cumbre",
                "025", MUNICIPALITY_LA_UNION, "026", MUNICIPALITY_LA_VICTORIA, "027", "Obando",
                "028", "Palmira", "029", "Pradera", "030", "Restrepo",
                "031", "Riofrío", "032", "Roldanillo", "033", MUNICIPALITY_SAN_PEDRO,
                "034", "Sevilla", "035", "Toro", "036", "Trujillo",
                "037", "Tuluá", "038", "Ulloa", "039", "Versalles",
                "040", "Vijes", "041", "Yotoco", "042", "Yumbo",
                "043", "Zarzal"
            ]),
            "81": ("Arauca", [
                "001", "Arauca", "002", "Arauquita", "003", "Cravo Norte",
                "004", "Fortul", "005", "Puerto Rondón", "006", "Saravena",
                "007", "Tame"
            ]),
            "85": ("Casanare", [
                "001", "Yopal", "002", "Aguazul", "003", "Chámeza",
                "004", "Hato Corozal", "005", "La Salina", "006", "Maní",
                "007", "Monterrey", "008", "Nunchía", "009", "Orocué",
                "010", "Paz de Ariporo", "011", "Pore", "012", "Recetor",
                "013", "Sabanalarga", "014", "Sácama", "015", "San Luís de Palenque",
                "016", "Támara", "017", "Tauramena", "018", "Trinidad",
                "019", "Villanueva"
            ]),
            "86": ("Putumayo", [
                "001", "Mocoa", "002", "Colón", "003", "Leguízamo",
                "004", "Orito", "005", "Puerto Asís", "006", "Puerto Caicedo",
                "007", "Puerto Guzmán", "008", MUNICIPALITY_SAN_FRANCISCO, "009", "San Miguel",
                "010", "Santiago", "011", "Sibundoy", "012", "Valle del Guamuez",
                "013", "Villagarzón"
            ]),
            "88": ("Archipiélago de San Andrés", [
                "001", MUNICIPALITY_SAN_ANDRES, "002", "Providencia"
            ]),
            "91": ("Amazonas", [
                "001", "Leticia", "002", "El Encanto", "003", "La Chorrera",
                "004", "La Pedrera", "005", MUNICIPALITY_LA_VICTORIA, "006", "Miriti - Paraná",
                "007", "Puerto Arica", "008", "Puerto Nariño", "009", "Puerto Santander",
                "010", "Tarapacá"
            ]),
            "94": ("Guainía", [
                "001", "Inírida", "002", "Barranco Minas", "003", "Mapiripana",
                "004", "San Felipe", "005", "Puerto Colombia", "006", "La Guadalupe",
                "007", "Cacahual", "008", "Pana Pana", "009", "Morichal"
            ]),
            "95": ("Guaviare", [
                "001", "San José del Guaviare", "002", "Calamar", "003", "El Retorno",
                "004", "Miraflores"
            ]),
            "97": ("Vaupés", [
                "001", "Mitú", "002", "Carurú", "003", "Pacoa",
                "004", "Taraira", "005", "Yavaraté"
            ]),
            "99": ("Vichada", [
                "001", "Puerto Carreño", "002", "La Primavera", "003", "Santa Rosalía",
                "004", "Cumaribo"
            ])
        }

        total_dept = 0
        total_mun = 0
        
        for codigo, (nombre_dept, municipios) in data.items():
            departamento, created = self._create_or_update_departamento(codigo, nombre_dept)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'" Departamento: {nombre_dept}'))
                total_dept += 1
            
            total_mun += self._process_municipios(departamento, municipios)

        self.stdout.write(self.style.SUCCESS(f'\n" Seed completado: {total_dept} departamentos, {total_mun} municipios creados.'))

    def _create_or_update_departamento(self, codigo: str, nombre_dept: str) -> tuple:
        """Crea o actualiza un departamento."""
        nombre_dept = _normalize_text(nombre_dept)
        departamento, created = Departamento.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre_dept}
        )

        if not created and departamento.nombre != nombre_dept:
            Departamento.objects.filter(pk=departamento.pk).update(nombre=nombre_dept)
            departamento.refresh_from_db()
            self.stdout.write(self.style.WARNING(f'• Departamento actualizado: {departamento.nombre}'))
        
        return departamento, created
    
    def _create_or_update_municipio(self, departamento, codigo_mun: str, nombre_mun: str) -> bool:
        """Crea o actualiza un municipio."""
        if not nombre_mun:
            return False
        
        nombre_mun = _normalize_text(nombre_mun)
        municipio, mun_created = Municipio.objects.get_or_create(
            departamento=departamento,
            codigo=codigo_mun,
            defaults={'nombre': nombre_mun}
        )

        if not mun_created and municipio.nombre != nombre_mun:
            Municipio.objects.filter(pk=municipio.pk).update(nombre=nombre_mun)
            self.stdout.write(self.style.WARNING(f'  • Municipio actualizado: {nombre_mun}'))
        
        return mun_created
    
    def _process_municipios(self, departamento, municipios: list) -> int:
        """Procesa los municipios de un departamento."""
        total_mun = 0
        i = 0
        
        while i < len(municipios):
            codigo_mun = municipios[i]
            nombre_mun = municipios[i + 1] if i + 1 < len(municipios) else ""
            
            if self._create_or_update_municipio(departamento, codigo_mun, nombre_mun):
                total_mun += 1
            
            i += 2
        
        return total_mun
