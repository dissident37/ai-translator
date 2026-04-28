# VPS Server — konstantinsittner.de

## Allgemeine Informationen

| Parameter    | Wert                            |
|--------------|---------------------------------|
| Anbieter     | IONOS                           |
| OS           | Ubuntu 22.04.5 LTS (Jammy)      |
| Kernel       | Linux 5.15.0-161-generic x86_64 |
| RAM          | 1,8 GB                          |
| Festplatte   | 78 GB (belegt 25 GB, frei 53 GB) |
| Swap         | Nicht vorhanden                 |
| Benutzer     | root                            |

## Domains

- `konstantinsittner.de` — Hauptdomain
- `songbook.konstantinsittner.de` — Songbook-Anwendung
- `umami.konstantinsittner.de` — Web-Analyse (Umami)

## Webserver

**Nginx 1.18.0**

Konfigurationen: `/etc/nginx/sites-enabled/`
- `default`
- `konstantinsittner.de`
- `songbook.konstantinsittner.de`
- `umami.konstantinsittner.de`

## Docker-Container

Alle Projekte werden über Docker Compose gestartet.

### Songbook (`/srv/songbook/`)
| Container          | Image          | Port      |
|--------------------|----------------|-----------|
| `songbook_app`     | `songbook-app` | 8447→8080 |
| `songbook_db`      | `postgres:16`  | 5432→5432 |
| `songbook_adminer` | `adminer`      | 8443→8080 |

- Stack: ASP.NET (dotnet) + PostgreSQL 16
- Adminer — Web-Oberfläche zur Datenbankverwaltung
- docker-compose: `/srv/songbook/docker-compose.yml`
- Quellcode: `/srv/songbook/app/`

### Umami (`/srv/umami/`)
| Container        | Image                                            | Port      |
|------------------|--------------------------------------------------|-----------|
| `umami-umami-1`  | `ghcr.io/umami-software/umami:postgresql-latest` | 3001→3000 |
| `umami-db-1`     | `postgres:16`                                    | intern    |

- Web-Analyse-Tool mit eigener Datenbank
- docker-compose: `/srv/umami/docker-compose.yml`

## VPN

**AmneziaVPN** (amnezia-xray)
- Installiert unter `/opt/amnezia/amnezia-xray`

## Verzeichnisstruktur

```
/srv/
├── songbook/
│   ├── docker-compose.yml
│   └── app/
│       └── deploy/
│           └── docker-compose.yml
└── umami/
    └── docker-compose.yml

/opt/
├── amnezia/
│   └── amnezia-xray/
└── containerd/

/etc/nginx/
└── sites-enabled/
    ├── default
    ├── konstantinsittner.de
    ├── songbook.konstantinsittner.de
    └── umami.konstantinsittner.de
```

## Deployment

- Projekte werden über **Docker Compose** deployed
- Konfigurationen liegen unter `/srv/<project>/`
- Nginx fungiert als Reverse Proxy vor den Containern

## Hinweise

- Swap ist deaktiviert — bei Speichermangel können Prozesse abstürzen
- PostgreSQL bei Songbook ist extern auf Port 5432 erreichbar — Firewall-Regeln prüfen
- In `/root/` befinden sich `server.json` und `vpn_link.txt` — möglicherweise VPN-Konfigurationen
