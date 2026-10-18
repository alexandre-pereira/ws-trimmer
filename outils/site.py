# SPDX-License-Identifier: ISC
"""Construit le site de présentation à partir du README : python outils/site.py [dossier de sortie]

Le site est le README rendu en HTML, avec une bannière, un sommaire, les fichiers STL à télécharger
et les images. Il existe en anglais (à la racine du site, la langue par défaut, depuis README.en.md)
et en français (dans fr/, depuis README.md) : ce qui change dans un README se reporte dans l'autre.
Il est reconstruit à chaque modification du dépôt par GitHub Actions (.github/workflows/pages.yml),
donc la page suit le dossier : ce qui change dans les README, stl/ ou apercu/ change sur le site.

L'habillage (wesoar.css, wesoar.svg, wesoar-mark.svg) est celui de tous les outils WeSoar : les
mêmes fichiers sont dans le dépôt de chaque outil. La police Mona Sans (mona-sans.woff2, licence SIL
OFL, avec mona-sans-OFL.txt) est servie par le site lui-même, sans passer par Google Fonts.

Le pied de page porte les mentions légales, tirées de EDITEUR et HEBERGEUR : la fabrication du site
signale les champs encore « à compléter ».
"""
import os, re, shutil, sys, html, json
import markdown

OUTILS = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(OUTILS)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, "_site")
DEPOT = "https://github.com/alexandre-pereira/ws-trimmer"
# la première langue est à la racine du site, les autres dans un dossier à leur nom
LANGUES = ["en", "fr"]
# clé du localStorage qui retient la langue choisie par le visiteur
CLE_LANGUE = "wf-lang"
# image des aperçus de lien (réseaux sociaux, messageries)
IMAGE_APERCU = "apercu/banc_ouvert_avant.png"

# éditeur du site, pour les mentions légales (LCEN, art. 1-1) : la société WeSoar, qui diffuse le
# banc. Ce qui n'est pas encore connu porte la marque A_COMPLETER (« […à compléter] ») : la page
# l'affiche tel quel et la fabrication du site le signale. Capital, siège et immatriculation sont à
# reporter depuis l'extrait Kbis ; le téléphone est obligatoire pour une société.
A_COMPLETER = "à compléter"
EDITEUR = {
    "nom": "WeSoar",
    "forme": "SASU",
    "capital": "[capital %s]" % A_COMPLETER,                # capital social, ex. « 1 000 € »
    "siege": "[adresse du siège %s]" % A_COMPLETER,         # adresse du siège social
    "immatriculation": "RCS [ville %s] [SIREN %s]" % (A_COMPLETER, A_COMPLETER),  # ex. « RCS Annecy 123 456 789 »
    "telephone": "[téléphone %s]" % A_COMPLETER,
    "tva": "",            # numéro de TVA intracommunautaire, s'il existe ; vide, il n'est pas écrit
    "email": "alex@wesoar.fr",
    "directeur": "Alexandre Pereira",
}
# hébergeur du site (GitHub Pages)
HEBERGEUR = {
    "nom": "GitHub, Inc.",
    "adresse": "88 Colin P. Kelly Jr. Street, San Francisco, CA 94107",
    "telephone": "+1 877 448 4820",
}
# marques citées dans les README et les notes
MARQUES = "Leica, DISTO, Bosch, HOTO, JLC3DP, OpenBuilds, V-Slot"


def ligne_editeur(e, capital, siege, tva, telephone):
    """L'éditeur sur une ligne, sans les champs vides ; les mots de liaison sont ceux de la langue"""
    return ", ".join(x for x in [
        e["nom"] + (", " + e["forme"] if e["forme"] else "") + (capital + e["capital"] if e["capital"] else ""),
        e["siege"] and siege + e["siege"],
        e["immatriculation"],
        e["tva"] and tva + e["tva"],
        e["telephone"] and telephone + e["telephone"],
        '<a href="mailto:%s">%s</a>' % (e["email"], e["email"]),
    ] if x)

# « outils » : les autres outils WeSoar, au pied de page. Ils ne sont pas tous gratuits : Wing Trim a un
# compte gratuit limité (10 mesures par mois, certaines voiles EN C, EN D et CCC ; les autres demandent
# un compte pro), d'où « compte gratuit limité ».
TEXTES = {
    "en": {
        "readme": "README.en.md",
        "locale": "en_GB",
        "sous_titre": "Measure your lines with a laser, under 5 kg, with two 3D-printed parts: 7 files for the bench, a holder sized for your distance meter, ≈ €15 of hardware.",
        "etiquette": "Free tool to 3D-print",
        "telecharger": "Download the STL files",
        "source": "Source code",
        "sommaire": "Contents",
        "fichiers": "One STL file per part, already oriented for printing, in millimetres. Recommended materials are further down.",
        "supports_titre": "The laser holder, in the version for your distance meter",
        "supports": "Leica DISTO and Bosch models under €500, at the manufacturer's dimensions (length × width × thickness) plus 0.5 mm of clearance. Other distance meter: see further down.",
        "taille": "%d kB",
        "cree": "Developed and offered free of charge by WeSoar.",
        "autres": "Other WeSoar tools:",
        "outils": [("https://trim.wesoar.fr/", "Wing Trim, the app to measure and trim your lines (limited free account)"),
                   ("https://soundings.wesoar.fr/", "PG Soundings, the free-flight forecast inside Windy"),
                   ("https://viewer.wesoar.fr/", "Viewer 3D, to replay your flights over the terrain and share them")],
        "pied": "Page built automatically from the repository: it reflects the files as of the last change.",
        "mentions_titre": "Legal notice",
        "mentions": lambda e, h, base: [
            "<b>Publisher</b>: %s. Publication director: %s, president."
            % (ligne_editeur(e, " with a share capital of ", "registered office: ", "VAT ", "phone "), e["directeur"]),
            "<b>Host</b>: %s (GitHub Pages), %s, United States, phone %s." % (h["nom"], h["adresse"], h["telephone"]),
            "<b>Personal data</b>: this page sets no cookie, does not measure its audience and loads nothing from other sites. "
            "It only keeps, in your browser, the language you chose. As with any web page, the host (GitHub) receives the "
            "visitor's IP address.",
            "<b>Intellectual property</b>: © 2026 WeSoar SASU. The bench is designed by Alexandre Pereira; WeSoar SASU owns "
            'the rights and distributes it. Its OpenSCAD models and STL files are published under the '
            '<a href="https://ohwr.org/cern_ohl_s_v2.txt">CERN-OHL-S-2.0</a> licence, its code under the '
            '<a href="%s/blob/main/LICENSE">ISC licence</a>, its pictures, assembly diagrams, texts and distance meter dimensions '
            'under the <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> licence, '
            "crediting “Paraglider trimming bench, designed "
            "by Alexandre Pereira, © 2026 WeSoar SASU”, the file's licence and the repository link. The WeSoar name and logo "
            "belong to the publisher and are covered by none of these licences. The Mona Sans typeface is used under "
            'the <a href="%smona-sans-OFL.txt">SIL Open Font License</a>. %s and the other brands cited belong to their '
            "owners; the bench is not affiliated with them." % (DEPOT, base, MARQUES),
            "<b>Liability</b>: a first unit of the bench has been printed and tried by its author; these trials remain limited "
            "and are neither a certification nor a validation by a workshop. The bench is provided free of charge, without "
            "warranty to the extent permitted by law, and used at your own risk; this does not exclude liability for personal "
            "injury, liability for defective products, or liability for fraud or gross negligence. Trimming a wing must follow its manufacturer's values and procedures, and a measuring error can change "
            "how the wing behaves in flight: have any re-trim checked by a qualified workshop. The bench stays on the table only "
            "because the line pulls on it: if the line goes slack, the 5 kg water bag tips it over and it falls. Set the cord so "
            "that the bag rests on the floor as soon as the line slackens, and keep everyone out from under the bag.",
        ],
        "langue": "Language",
    },
    "fr": {
        "readme": "README.md",
        "locale": "fr_FR",
        "sous_titre": "Mesurer ses suspentes au laser, sous 5 kg, avec deux pièces imprimées en 3D : 7 fichiers pour le banc, un support à la taille de votre télémètre, ≈ 15 € de quincaillerie.",
        "etiquette": "Outil gratuit à imprimer en 3D",
        "telecharger": "Télécharger les fichiers STL",
        "source": "Code source",
        "sommaire": "Sommaire",
        "fichiers": "Un fichier STL par pièce, déjà orienté pour l'impression, en millimètres. Les matières conseillées sont plus bas.",
        "supports_titre": "Le support du laser, dans la version de votre télémètre",
        "supports": "Leica DISTO et Bosch à moins de 500 €, aux cotes du constructeur (longueur × largeur × épaisseur) plus 0,5 mm de jeu. Autre télémètre : voir plus bas.",
        "taille": "%d Ko",
        "cree": "Développé et offert gratuitement par WeSoar.",
        "autres": "Autres outils WeSoar :",
        "outils": [("https://trim.wesoar.fr/", "Wing Trim, l'application de mesure et de calage des suspentes (compte gratuit limité)"),
                   ("https://soundings.wesoar.fr/fr/", "PG Soundings, la prévision du vol libre dans Windy"),
                   ("https://viewer.wesoar.fr/", "Viewer 3D, pour revoir vos vols sur le relief et les partager")],
        "pied": "Page construite automatiquement à partir du dépôt : elle reflète l'état des fichiers au dernier changement.",
        "mentions_titre": "Mentions légales",
        "mentions": lambda e, h, base: [
            "<b>Éditeur</b> : %s. Directeur de la publication : %s, président."
            % (ligne_editeur(e, " au capital de ", "siège social : ", "TVA ", "téléphone "), e["directeur"]),
            "<b>Hébergeur</b> : %s (GitHub Pages), %s, États-Unis, téléphone %s." % (h["nom"], h["adresse"], h["telephone"]),
            "<b>Données personnelles</b> : cette page ne pose aucun cookie, ne mesure pas l'audience et ne charge rien depuis "
            "d'autres sites. Elle retient seulement, dans votre navigateur, la langue choisie. Comme pour toute page web, "
            "l'hébergeur (GitHub) reçoit l'adresse IP du visiteur.",
            "<b>Propriété intellectuelle</b> : © 2026 WeSoar SASU. Le banc est conçu par Alexandre Pereira ; WeSoar SASU en "
            'détient les droits et le diffuse. Ses modèles OpenSCAD et ses fichiers STL sont publiés sous licence '
            '<a href="https://ohwr.org/cern_ohl_s_v2.txt">CERN-OHL-S-2.0</a>, son code sous <a href="%s/blob/main/LICENSE">licence '
            'ISC</a>, ses images, schémas de montage, textes et cotes des télémètres sous licence '
            '<a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">CC BY-SA 4.0</a>, '
            "en citant « Banc de calage parapente, conçu par "
            "Alexandre Pereira, © 2026 WeSoar SASU », la licence du fichier et le lien du dépôt. Le nom et le logo WeSoar "
            "appartiennent à l'éditeur et n'entrent dans aucune de ces licences. La police Mona Sans est utilisée sous "
            '<a href="%smona-sans-OFL.txt">licence SIL Open Font License</a>. %s et les autres marques citées appartiennent '
            "à leurs titulaires ; le banc n'a aucun lien avec eux." % (DEPOT, base, MARQUES),
            "<b>Responsabilité</b> : un premier exemplaire du banc a été imprimé et essayé par son auteur ; ces essais restent "
            "limités et ne valent ni certification ni validation par un atelier. Le banc est fourni gratuitement, sans garantie "
            "dans les limites permises par la loi, et utilisé aux risques de l'utilisateur ; cela n'exclut ni la responsabilité "
            "pour les dommages corporels, ni celle du fait des produits défectueux, ni celle due au dol ou à la faute lourde. "
            "Le calage d'une aile doit respecter les valeurs et les procédures de son constructeur, "
            "et une erreur de mesure peut modifier le comportement de l'aile en vol : faites contrôler tout recalage par un "
            "atelier qualifié. Le banc ne tient sur la table que par la traction de la suspente : suspente relâchée, la poche "
            "de 5 kg le fait basculer et il tombe. Réglez la cordelette pour que la poche repose au sol dès que la suspente "
            "mollit, et ne laissez personne sous la poche.",
        ],
        "langue": "Langue",
    },
}

# ce qui est propre à cette page ; le reste vient de la feuille commune des outils WeSoar
STYLE = """
.tt-vues { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 12px; }
.tt-vues figure { margin: 0; padding: 10px; }
.tt-vues img { display: block; width: 100%; border-radius: 8px; background: #fff; }
.tt-vues figcaption { margin-top: 8px; padding: 0 4px 2px; font-size: .88rem; font-weight: 600; }
.tt-cols { display: grid; grid-template-columns: minmax(0, 1fr); gap: 24px; margin-top: clamp(28px, 5vw, 44px); }
@media (min-width: 60rem) { .tt-cols { grid-template-columns: 14rem minmax(0, 1fr); gap: 32px; align-items: start; } .tt-sommaire { position: sticky; top: 16px; } }
.tt-sommaire { padding: 16px 18px; font-size: .9rem; }
.tt-sommaire h2 { margin: 0 0 8px; font-size: .74rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--wf-muted); }
.tt-sommaire ol { margin: 0; padding: 0; list-style: none; display: grid; gap: 6px; }
.tt-sommaire a { color: var(--wf-ink); text-decoration: none; }
.tt-sommaire a:hover { color: var(--wf-accent-strong); text-decoration: underline; }
.tt-fichiers { margin-bottom: 28px; scroll-margin-top: 16px; }
.tt-fichiers h2 { margin: 0 0 6px; }
.tt-fichiers ul + h2 { margin-top: 24px; }
.tt-fichiers p { margin: 0 0 14px; color: var(--wf-muted); }
.tt-fichiers ul { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr)); gap: 8px; }
.tt-fichiers li { margin: 0; }
.tt-fichiers .wf-btn { display: block; padding: 9px 12px; font: 600 .85rem var(--wf-mono); overflow-wrap: anywhere; }
.tt-fichiers .wf-btn small { display: block; margin-top: 2px; font: 400 .8rem var(--wf-font); color: var(--wf-muted); }
.tt-fichiers .tt-vue { display: inline-block; margin: 2px 0 0 4px; font-size: .82rem; }
.tt-avertissement { margin: 0 0 20px; padding: 14px 18px; border-left: 4px solid var(--wf-accent); border-radius: var(--wf-radius-s); background: var(--wf-tint); }
.tt-avertissement p { margin: 0; }
.tt-avertissement p + p { margin-top: 10px; }
.tt-mentions summary { cursor: pointer; color: var(--wf-ink); font-weight: 700; }
.tt-mentions p { margin: 8px 0 0; }
"""


def lire(*chemin):
    return open(os.path.join(*chemin), encoding="utf-8").read()


def vers(depuis, langue):
    """Adresse du dossier d'une langue, depuis la page d'une autre : « ./ », « fr/ » ou « ../ »"""
    if depuis == langue:
        return "./"
    return ("" if depuis == LANGUES[0] else "../") + ("" if langue == LANGUES[0] else langue + "/")


def banniere(readme):
    """Le titre et le tableau d'images du début du README passent dans la bannière.

    Rend le titre, les figures (image, texte de remplacement, légende), l'avertissement qui ouvre le
    README (une citation « > ») et le README sans eux.
    """
    readme = readme.replace("\r\n", "\n")
    titre = re.search(r"^# (.*)\n", readme).group(1).strip()
    readme = re.sub(r"^# .*\n", "", readme, count=1)
    # le lien vers le README de l'autre langue ne sert que sur GitHub : la page a son choix de langue
    readme = re.sub(r"^\[[^\]]*\]\(README(\.\w+)?\.md\)\s*\n", "", readme, count=1, flags=re.M)
    # l'avertissement passe en tête de la page, avant les fichiers à télécharger
    avertissement = ""
    citation = re.match(r"\s*((?:>[^\n]*\n)+)", readme)
    if citation:
        avertissement, readme = citation.group(1), readme[citation.end():]
    tableau = re.search(r"\n\|([^\n]*)\|\n\|---[^\n]*\n\|([^\n]*!\[[^\n]*)\|\n", readme)
    legendes = [c.strip() for c in tableau.group(1).split("|")]
    images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", tableau.group(2))
    readme = readme.replace(tableau.group(0), "\n\n", 1)
    return titre, [(src, alt, legende) for (alt, src), legende in zip(images, legendes)], avertissement, readme


def page(langue, logo, style, stls, lasers, site):
    t = TEXTES[langue]
    base = vers(langue, LANGUES[0])
    taille = lambda f: t["taille"] % round(os.path.getsize(os.path.join(RACINE, "stl", f)) / 1024)
    titre, figures, avertissement, readme = banniere(lire(RACINE, t["readme"]))
    avertissement = markdown.markdown(avertissement).replace("<blockquote>", '<blockquote class="tt-avertissement">')
    corps = markdown.markdown(readme, extensions=["tables", "fenced_code", "toc", "sane_lists"],
                              extension_configs={"toc": {"toc_depth": "2"}})
    corps = corps.replace("<table>", '<div class="wf-scroll"><table>').replace("</table>", "</table></div>")
    # les images et les STL sont à la racine du site, quelle que soit la langue
    corps = re.sub(r'(src|href)="(apercu|stl)/', r'\1="%s\2/' % base, corps)
    # sommaire : les titres de niveau 2
    titres = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', corps)
    sommaire = "".join('<li><a href="#%s">%s</a></li>' % (i, re.sub(r"<.*?>", "", h)) for i, h in titres)
    fichiers = "".join('<li><a class="wf-btn wf-btn--ghost" href="%sstl/%s" download>%s<small>%s</small></a></li>'
                       % (base, f, html.escape(f), taille(f)) for f in stls)
    # le support du laser : une version par télémètre de outils/lasers.json
    supports = ""
    for m in lasers:
        f = "support_laser_%s.stl" % m["slug"]
        if not os.path.exists(os.path.join(RACINE, "stl", f)):
            continue
        supports += ('<li><a class="wf-btn wf-btn--ghost" href="%sstl/%s" download>%s<small>%s × %s × %s mm · %s</small></a>'
                     % (base, f, html.escape(m["modele"]), m["longueur"], m["largeur"], m["epaisseur"], taille(f)))
        if os.path.exists(os.path.join(RACINE, "apercu", "support_laser_%s.png" % m["slug"])):
            supports += '<a class="tt-vue" href="%sapercu/support_laser_%s.png">image</a>' % (base, m["slug"])
        supports += "</li>"
    vues = "".join('<figure class="wf-card"><img src="%s%s" alt="%s"><figcaption>%s</figcaption></figure>'
                   % (base, src, html.escape(alt), html.escape(legende)) for src, alt, legende in figures)
    choix = "".join('<a href="%s" lang="%s" hreflang="%s"%s onclick="try{localStorage.setItem(\'%s\',\'%s\')}catch(e){}">%s</a>'
                    % (vers(langue, l), l, l, ' aria-current="page"' if l == langue else "", CLE_LANGUE, l, l.upper())
                    for l in LANGUES)
    outils = "".join('<li><a href="%s">%s</a></li>' % (url, html.escape(nom)) for url, nom in t["outils"])
    mentions = "\n".join("<p>%s</p>" % ligne for ligne in t["mentions"](EDITEUR, HEBERGEUR, base))
    # la page par défaut envoie vers sa langue le visiteur qui en a choisi une autre, ou dont le
    # navigateur est dans une autre langue du site tant qu'il n'a rien choisi
    renvoi = ""
    if langue == LANGUES[0]:
        renvoi = ("<script>try{var l=localStorage.getItem('%s')||(navigator.language||'').slice(0,2).toLowerCase();"
                  "if(%s.indexOf(l)>=0)location.replace(l+'/'+(location.protocol=='file:'?'index.html':'')+location.hash)}catch(e){}</script>\n"
                  % (CLE_LANGUE, json.dumps(LANGUES[1:])))
    # balises des aperçus de lien : elles demandent des adresses complètes, donc le domaine du site
    social = ['<meta property="og:type" content="website">',
              '<meta property="og:locale" content="%s">' % t["locale"],
              '<meta property="og:title" content="%s">' % html.escape(titre),
              '<meta property="og:description" content="%s">' % html.escape(t["sous_titre"])]
    if site:
        adresse = lambda l: "%s/%s" % (site, "" if l == LANGUES[0] else l + "/")
        social += ['<link rel="canonical" href="%s">' % adresse(langue)]
        social += ['<link rel="alternate" hreflang="%s" href="%s">' % (l, adresse(l)) for l in LANGUES]
        social += ['<link rel="alternate" hreflang="x-default" href="%s">' % adresse(LANGUES[0]),
                   '<meta property="og:url" content="%s">' % adresse(langue),
                   '<meta property="og:image" content="%s/%s">' % (site, IMAGE_APERCU)]
    social = "\n".join(social)

    return f"""<!doctype html>
<html lang="{langue}">
<head>
<meta charset="utf-8">
{renvoi}<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titre)}</title>
<meta name="description" content="{html.escape(t["sous_titre"])}">
<meta name="theme-color" content="#f5f7f9">
{social}
<link rel="icon" type="image/svg+xml" href="{base}favicon.svg">
<link rel="preload" href="{base}mona-sans.woff2" as="font" type="font/woff2" crossorigin>
<style>@font-face {{ font-family: 'Mona Sans'; src: url('{base}mona-sans.woff2') format('woff2'); font-weight: 400 800; font-display: swap; }}
{style}</style>
</head>
<body>
<header class="wf-top">
<span class="wf-brand">{logo}</span>
<nav class="wf-lang" aria-label="{t["langue"]}">{choix}</nav>
</header>
<main class="wf-page">
<div class="wf-hero">
<span class="wf-eyebrow">{t["etiquette"]}</span>
<h1 class="wf-title">{html.escape(titre)}</h1>
<p class="wf-lead">{html.escape(t["sous_titre"])}</p>
<div class="wf-actions">
<a class="wf-btn" href="#stl">{t["telecharger"]}</a>
<a class="wf-btn wf-btn--ghost" href="{DEPOT}">{t["source"]}</a>
</div>
</div>
<div class="tt-vues">{vues}</div>
<div class="tt-cols">
<nav class="tt-sommaire wf-card"><h2>{t["sommaire"]}</h2><ol>{sommaire}</ol></nav>
<div class="wf-prose">
{avertissement}
<section class="tt-fichiers wf-card" id="stl"><h2>{t["telecharger"]}</h2>
<p>{t["fichiers"]}</p>
<ul>{fichiers}</ul>
<h2>{t["supports_titre"]}</h2>
<p>{t["supports"]}</p>
<ul>{supports}</ul></section>
{corps}
</div>
</div>
</main>
<footer class="wf-foot"><div class="wf-foot-in">
<div class="wf-made">{logo}<span>{t["cree"]}</span></div>
<ul class="wf-tools"><li>{t["autres"]}</li>{outils}</ul>
<p>{t["pied"]}</p>
<details class="tt-mentions" id="legal"><summary>{t["mentions_titre"]}</summary>
{mentions}
</details>
<!-- Le lien #legal ouvre les mentions, repliées sinon -->
<script>if(location.hash=='#legal')document.getElementById('legal').open=true</script>
</div></footer>
</body>
</html>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for d in ("stl", "apercu"):
        dst = os.path.join(OUT, d)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(RACINE, d), dst)
    stls = sorted(f for f in os.listdir(os.path.join(RACINE, "stl")) if f.endswith(".stl") and not f.startswith("support_laser_"))
    lasers = json.loads(lire(OUTILS, "lasers.json"))
    site = ""
    cname = os.path.join(RACINE, "CNAME")
    if os.path.exists(cname):
        shutil.copy(cname, OUT)
        site = "https://" + lire(cname).strip()
    shutil.copy(os.path.join(OUTILS, "wesoar-mark.svg"), os.path.join(OUT, "favicon.svg"))
    # la police est servie avec la page, et sa licence (SIL OFL) l'accompagne
    for f in ("mona-sans.woff2", "mona-sans-OFL.txt"):
        shutil.copy(os.path.join(OUTILS, f), OUT)

    # le logo WeSoar est dessiné dans la page, pour prendre la couleur du texte
    logo = lire(OUTILS, "wesoar.svg").strip().replace("<svg ", '<svg class="wf-logo" ', 1)
    style = lire(OUTILS, "wesoar.css") + STYLE
    for langue in LANGUES:
        dossier = OUT if langue == LANGUES[0] else os.path.join(OUT, langue)
        os.makedirs(dossier, exist_ok=True)
        open(os.path.join(dossier, "index.html"), "w", encoding="utf-8", newline="\n").write(
            page(langue, logo, style, stls, lasers, site))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print("site écrit dans", OUT, ":", len(stls), "fichiers STL,", len(lasers), "télémètres,", ", ".join(LANGUES))
    # mentions légales : les champs encore à compléter ; GitHub affiche l'avertissement en tête de la publication
    noms = {"capital": "capital", "siege": "siège social", "immatriculation": "immatriculation (RCS)", "telephone": "téléphone"}
    manque = [noms.get(k, k) for k, v in EDITEUR.items() if A_COMPLETER in v or (k in noms and not v)]
    if manque:
        print("%sMentions légales incomplètes, à remplir dans EDITEUR (outils/site.py) : %s"
              % ("::warning::" if os.environ.get("GITHUB_ACTIONS") else "Attention : ", ", ".join(manque)), file=sys.stderr)


if __name__ == "__main__":
    main()
