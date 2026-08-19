import os
import time
import random
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.abspath(
    os.path.expanduser(
        os.getenv("EDGE_USER_DATA_DIR", os.path.join(BASE_DIR, ".edge-playwright-profile"))
    )
)
EDGE_CHANNEL = os.getenv("EDGE_CHANNEL", "msedge")
LAUNCH_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_LAUNCH_TIMEOUT_MS", "30000"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_NAVIGATION_TIMEOUT_MS", "30000"))

SAMSUNG_A16_5G_CONF = {
    "user_agent": "Mozilla/5.0 (Linux; Android 16; SM-A166M/DS) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "viewport": {"width": 360, "height": 780},
    "device_scale_factor": 3.0,
    "is_mobile": True,
    "has_touch": True,
}

DESKTOP_CONF = {
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 1.0,
    "is_mobile": False,
    "has_touch": False,
}

ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-first-run",
    "--no-default-browser-check",
]

def hideFootPrintBot(context):
    """Inyect JavaScript for hiding the automation flags natively."""
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

ROJO = "\033[31m"
VERDE = "\033[32m"
RESET = "\033[0m"


def launchEdgeContext(pw, device_conf):
    os.makedirs(PROFILE_PATH, exist_ok=True)
    print(f"[i] Edge user data dir: {PROFILE_PATH}", flush=True)

    context = pw.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        channel=EDGE_CHANNEL,
        headless=False,
        args=ARGS,
        ignore_default_args=["--enable-automation"],
        timeout=LAUNCH_TIMEOUT_MS,
        **device_conf
    )
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    context.set_default_timeout(NAVIGATION_TIMEOUT_MS)
    hideFootPrintBot(context)
    return context


def activePage(context):
    page = context.new_page()
    page.bring_to_front()
    return page


KEYWORDS = [
    'fernando alonso',
    'resorts',
    'airbus a380',
    'python',
    'boeing 787X',
    'spotify',
    'Linux Fedora',
    'Linux Ubuntu',
    'ciencia',
    'Teclados 70%',
    'futbol americano',
    'como instalar windows 11',
    'nicolas maduro 2026',
    'que le paso a nicolas maduro',
    'Samsung galaxy A36 5G',
    'Samsung galaxy S26 Pro',
    'Intel core Ultra x9',
    'nvidia volvera a fabricar las rtx 3000-4000',
    'CS2',
    'minecraft',
    'petronas',
    'steven jobs',
    'Luis abinader',
    'pendrive de 128gb',
    'airpods pro',
    'camaras 12K',
    'Sora AI',
    'platanos',
    'real racing 4',
    'orquideas',
    'ropas',
    'David',
    'dell P2422HE',
    'thunderbolt',
    'como recuperar mi cuenta',
    'Funk',
    'hora en brazil',
    'swiches marrones para teclado',
    'antec',
    'nissan',
    'toyota',
    'F1 2026',
    'arquitectura hibrida',
    'tiktok',
    'youtube',
    'linux from scratch',
    'galaxy S25',
    'tecnología',
    'inteligencia artificial',
    'recetas de cocina',
    'viajes económicos',
    'noticias de hoy',
    'ejercicio en casa',
    'meditación guiada',
    'programación python',
    'diseño gráfico',
    'marketing digital',
    'finanzas personales',
    'criptomonedas',
    'historia universal',
    'astronomía',
    'psicología',
    'desarrollo personal',
    'idiomas gratis',
    'fotografía digital',
    'jardinería',
    'bricolaje',
    'decoración de interiores',
    'moda sostenible',
    'cambio climático',
    'energías renovables',
    'salud mental',
    'nutrición deportiva',
    'yoga para principiantes',
    'gestión del tiempo',
    'productividad',
    'libros recomendados',
    'películas 2026',
    'series de moda',
    'videojuegos',
    'e-sports',
    'gadgets',
    'ciberseguridad',
    'blockchain',
    'realidad virtual',
    'teletrabajo',
    'emprendimiento',
    'startups',
    'ecommerce',
    'ventas online',
    'redes sociales',
    'seo',
    'sem',
    'copywriting',
    'diseño web',
    'ux ui',
    'machine learning',
    'big data',
    'computación en la nube',
    'internet de las cosas',
    'robótica',
    'biotecnología',
    'nanotecnología',
    'física cuántica',
    'literatura clásica',
    'poesía',
    'filosofía',
    'sociología',
    'antropología',
    'geografía',
    'clima',
    'fauna silvestre',
    'mascotas',
    'entrenamiento canino',
    'acuariofilia',
    'senderismo',
    'camping',
    'supervivencia',
    'fotografía de paisajes',
    'edición de video',
    'música lo-fi',
    'instrumentos musicales',
    'teoría musical',
    'dibujo técnico',
    'pintura al óleo',
    'escultura',
    'arquitectura moderna',
    'urbanismo',
    'transporte eléctrico',
    'automóviles autónomos',
    'exploración espacial',
    'marte',
    'agujeros negros',
    'biología marina',
    'oceanografía',
    'ecología',
    'reciclaje',
    'compostaje',
    'minimalismo',
    'estilo de vida',
    'viajes de aventura',
    'gastronomía local',
    'repostería',
    'coctelería',
    'vinos',
    'café de especialidad',
    'técnicas de estudio',
    'precio dolar republica dominicana hoy',
    'noticias diario libre hoy',
    'clima santo domingo mañana',
    'quien gano el f1 hoy',
    'mejores neumaticos real racing 3',
    'porque retiraron real racing 3 de la store',
    'como optimizar samsung a16 5g',
    'caracteristicas del procesador i3',
    'mejores teclados mecanicos baratos',
    'como aprender backend con python',
    'libreria selenium python tutorial',
    'que es un endpoint en una api',
    'receta de locrio de pollo dominicano',
    'historia de la independencia dominicana',
    'puntos turisticos punta cana',
    'como subir de nivel en roblox rapido',
    'esteban david',
    'mejores mapas de parkour roblox',
    'precio de memoria ram 16gb ddr4',
    'diferencia entre hdd y ssd kingston',
    'como limpiar un ventilador de pc',
    'resultado del sorteo de la loteria nacional',
    'itbis republica dominicana que es',
    'ofertas de supermercados hoy',
    'como configurar microsoft edge para puntos',
    'errores comunes en scripts de selenium',
    'como usar time sleep en python',
    'noticias sobre nicolas maduro hoy',
    'elecciones venezuela 2026 pronostico',
    'situacion economica venezuela actual',
    'mejores peliculas de netflix enero 2026',
    'estrenos de cine esta semana',
    'como hacer una base de datos en sql',
    'ventajas de usar fibra optica',
    'como mejorar el ping en juegos online',
    'que es el modo desarrollador en android',
    'accesorios para samsung galaxy a16',
    'mejores fundas para celulares samsung',
    'precio de tarjetas graficas usadas',
    'como armar una pc gamer economica',
    'CI/CD',
    'pipeline',
    'Docker',
    'Kubernetes',
    'Jenkins',
    'Terraform',
    'Ansible',
    'Puppet',
    'Chef',
    'Git',
    'GitHub',
    'GitLab',
    'Bitbucket',
    'ArgoCD',
    'Helm',
    'container',
    'microservicio',
    'orquestación',
    'automatización',
    'monitoreo',
    'logging',
    'alerting',
    'Prometheus',
    'Grafana',
    'Datadog',
    'ELK',
    'Splunk',
    'infraestructura',
    'IaC',
    'nube',
    'AWS',
    'Azure',
    'GCP',
    'serverless',
    'lambda',
    'escalabilidad',
    'resiliencia',
    'SRE',
    'observabilidad',
    'trazabilidad',
    'integración',
    'entrega',
    'despliegue',
    'rollback',
    'rollout',
    'blue-green',
    'canary',
    'feature flag',
    'A/B testing',
    'testing',
    'QA',
    'SAST',
    'DAST',
    'OWASP',
    'DevSecOps',
    'secrets',
    'vault',
    'certificado',
    'mTLS',
    'zero trust',
    'load balancer',
    'proxy',
    'Nginx',
    'Traefik',
    'service mesh',
    'Istio',
    'Linkerd',
    'caching',
    'Redis',
    'RabbitMQ',
    'Kafka',
    'cola',
    'evento',
    'webhook',
    'API',
    'REST',
    'gRPC',
    'GitOps',
    'release',
    'versioning',
    'juegos parecidos a real racing 3 para android',
    'descargar mods para roblox',
    'perro',
    'galaxia',
    'reloj',
    'montaña',
    'nube',
    'teclado',
    'bosque',
    'espejo',
    'guitarra',
    'viento',
    'ciudad',
    'puente',
    'océano',
    'libro',
    'pintura',
    'café',
    'estatua',
    'planeta',
    'invierno',
    'fuego',
    'camino',
    'sombra',
    'vuelo',
    'piedra',
    'arena',
    'cristal',
    'jardín',
    'brújula',
    'portal',
    'trueno',
    'mariposa',
    'antena',
    'bosquejo',
    'moneda',
    'escudo',
    'flecha',
    'balcón',
    'cascada',
    'desierto',
    'esmeralda',
    'fuente',
    'gruta',
    'horizonte',
    'isla',
    'jungla',
    'kiwi',
    'laberinto',
    'mañana',
    'noche',
    'orquídea',
    'pasillo',
    'queso',
    'relámpago',
    'selva',
    'túnel',
    'universo',
    'valle',
    'whisky',
    'xilófono',
    'yate',
    'zafiro',
    'átomo',
    'barco',
    'calle',
    'delfín',
    'elefante',
    'farola',
    'globo',
    'hielo',
    'imán',
    'jaula',
    'koala',
    'lámpara',
    'martillo',
    'neblina',
    'otoño',
    'parque',
    'quásar',
    'rueda',
    'satélite',
    'tigre',
    'uvas',
    'ventana',
    'yoga',
    'zorro',
    'acero',
    'brisa',
    'cable',
    'danza',
    'energía',
    'fruta',
    'grano',
    'huerto',
    'idea',
    'juego',
    'kilómetro',
    'luna',
    'meta',
    'nieve',
    'olivo',
    'perla',
    'química',
    'rayo',
    'sol',
    'torre',
    'utopía',
    'vapor',
    'web',
    'xenón',
    'yodo',
    'zona',
    'abeja',
    'botón',
    'carro',
    'disco',
    'esfera',
    'faro',
    'gente',
    'hoja',
    'incienso',
    'jarra',
    'ladrillo',
    'música',
    'nido',
    'órbita',
    'papel',
    'quesera',
    'ritmo',
    'seda',
    'trigo',
    'unión',
    'velas',
    'wifi',
    'yema',
    'zueco',
    'aceite',
    'búho',
    'clavo',
    'dedo',
    'estufa',
    'fresa',
    'grifo',
    'humo',
    'iglú',
    'joya',
    'lupa',
    'miel',
    'naranja',
    'ola',
    'pino',
    'quince',
    'rosa',
    'sal',
    'tren',
    'uva',
    'vaso',
    'yuyo',
    'zeta',
    'arco',
    'blanco',
    'clima',
    'dulce',
    'extra',
    'fina',
    'gota',
    'hilo',
    'isla',
    'jefe',
    'lima',
    'muro',
    'neto',
    'oro',
    'paz',
    'rama',
    'sur',
    'taza',
    'universidad',
    'viento',
    'wafle',
    'xilófono',
    'yegua',
    'zorro',
    'copilot',
    'AMD Ryzen 9 7950X',
    'Intel Core i9-13900K',
    'NVIDIA GeForce RTX 4090',
    'Apple M2 Max',
    'Samsung Galaxy S25 Ultra',
    'PlayStation 5 Pro',
    'Xbox Series X2',
    'Nvidia RTX Spark',
    '8192 MB',
    'AMD Ryzen 5 8600G',
    'Radeon 760m',
    'Samsung PM9A1a 1TB',
    'microsoft surface',
    'fantech',
    'A620m A pro',
    'KZ Edx pro X',
    'Gskill Ripjaws S5 16GB DDR5 6000MHz',
    'Trinary CPUs',
    'claude IA',
    'cursor',
    'Visual studio code'   
]

def execMobileSearch():
    print("\n(+) Starting Bing Rewards Bot (A16 5G Mobile mode)...")

    with sync_playwright() as pw:
        context = launchEdgeContext(pw, SAMSUNG_A16_5G_CONF)
        page = activePage(context)

        try:
            print("[x] Connecting to Microsoft Bing...")
            page.goto("https://www.bing.com", wait_until="domcontentloaded")
            time.sleep(random.uniform(2.35, 3.35))

            random.shuffle(KEYWORDS)
            MOBILEDAILYSEARCH = KEYWORDS[:20]

            for idx, keyword in enumerate(MOBILEDAILYSEARCH, 1):
                print(f"-- [{idx}/{len(MOBILEDAILYSEARCH)}] Searching:\n'{keyword}...'")

                search_url = f"https://www.bing.com/search?q={quote_plus(keyword)}"
                page.goto(search_url, wait_until="domcontentloaded")

                wait_time = random.uniform(4.35, 6.35)
                time.sleep(wait_time)

            print(f"\n{VERDE}[✓] Searching cycle has been completed succesfully.{RESET}")

        except Exception as e:
            print(f"\n{ROJO}[ER]: Error during Mobile bot execution at: {e}{RESET}")

        finally:
            context.close()


def execDesktopSearch():
    print("\n(+) Starting Bing Rewards Bot (Desktop Mode)...")

    with sync_playwright() as pw:
        context = launchEdgeContext(pw, DESKTOP_CONF)
        page = activePage(context)

        try:
            print("[x] Connecting to Microsoft Bing...")
            page.goto("https://www.bing.com", wait_until="domcontentloaded")
            time.sleep(random.uniform(2.35, 3.35))

            random.shuffle(KEYWORDS)
            DAILYSEARCH = KEYWORDS[:31]

            for idx, keyword in enumerate(DAILYSEARCH, 1):
                print(f"-- [{idx}/{len(DAILYSEARCH)}] Searching (Desktop):\n'{keyword}...'")

                search_url = f"https://www.bing.com/search?q={quote_plus(keyword)}"
                page.goto(search_url, wait_until="domcontentloaded")

                wait_time = random.uniform(4.00, 6.50)
                time.sleep(wait_time)
                

            print(f"\n{VERDE}[✓] Desktop searching cycle has been completed successfully.{RESET}")
            return True

        except Exception as e:
            print(f"\n{ROJO}[ER]: Error during desktop bot execution at: {e}{RESET}")
            return False

        finally:
            context.close()

if __name__ == "__main__":
    #if not execDesktopSearch():
        #raise SystemExit(1)

    print("\n[$] Intermission: Profile switching in 3 seconds...")
    time.sleep(3)

    if not execMobileSearch():
        raise SystemExit(1)