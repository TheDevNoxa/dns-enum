# 🌐 dns-enum

Outil d'énumération DNS et de découverte de sous-domaines — projet éducatif réalisé dans le cadre du Bac Pro CIEL.

## Fonctionnalités

- Récupération de tous les enregistrements DNS (A, AAAA, MX, NS, TXT, SOA, CNAME…)
- Tentative de transfert de zone AXFR (zone transfer)
- Bruteforce de sous-domaines avec wordlist personnalisable
- Multi-threadé pour de meilleures performances
- Wordlist intégrée de 50+ sous-domaines communs

## Installation

```bash
git clone https://github.com/thedevnoxa/dns-enum
cd dns-enum
pip install -r requirements.txt
```

**requirements.txt**
```
dnspython>=2.4.0
```

## Utilisation

```bash
# Enumération complète avec wordlist intégrée
python3 dns_enum.py -d example.com

# Avec wordlist personnalisée
python3 dns_enum.py -d example.com -w wordlist.txt

# Juste les enregistrements DNS, sans bruteforce
python3 dns_enum.py -d example.com --no-bruteforce

# Sans tentative de zone transfer
python3 dns_enum.py -d example.com --no-axfr
```

## Exemple de sortie

```
[*] Enumerating DNS records for example.com ...
[*] Attempting zone transfer ...
[*] Bruteforcing subdomains (50 words, 50 threads) ...
  [+] api.example.com                              93.184.216.34
  [+] mail.example.com                             93.184.216.100
  [+] www.example.com                              93.184.216.34

=================================================================
  DNS ENUMERATION — example.com
=================================================================

  [ DNS Records ]

  A        93.184.216.34
  MX       0 mail.example.com.
  NS       ns1.example.com.
  TXT      "v=spf1 -all"

  [ Subdomains found: 3 ]

  api.example.com                              → 93.184.216.34
  mail.example.com                             → 93.184.216.100
  www.example.com                              → 93.184.216.34
=================================================================
```

## ⚠️ Avertissement légal

Usage **éducatif uniquement**. N'effectuez de reconnaissance DNS que sur des domaines vous appartenant ou pour lesquels vous avez une autorisation explicite.

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

---
*Projet réalisé par [Noxa](https://github.com/thedevnoxa) — Bac Pro CIEL*
