# Outils de génération

Scripts qui produisent les STL, les images d'aperçu et les schémas de montage.
OpenSCAD n'a pas besoin d'être installé : le rendu passe par sa version WebAssembly.

À lancer depuis ce dossier :

```
npm install openscad-wasm-prebuilt     # une seule fois
node generer_stl.mjs                   # STL dans ../stl, pièces d'assemblage dans ./asm, contrôles d'interférence
python render2.py                      # une image par STL + vues d'assemblage, dans ../apercu
python schema.py                       # schémas de montage avec la visserie, dans ../apercu
```

Python a besoin de `numpy` et `Pillow`. Les positions de la visserie dans `schema.py`
reprennent les cotes de `../scad/banc.scad` : si le modèle change, les mettre à jour.

## Licences

Ces scripts (`*.py`, `generer_stl.mjs`) sont sous licence ISC, comme l'indique le fichier
[LICENSE](../LICENSE) à la racine du dépôt ; chacun le dit en tête (`SPDX-License-Identifier: ISC`).
Ce dossier contient aussi des fichiers sous d'autres licences : `LISEZMOI.md` et `lasers.json`
sous CC BY-SA 4.0, la police Mona Sans sous SIL OFL 1.1 (voir plus bas), et le logo WeSoar
(`wesoar.svg`, `wesoar-mark.svg`), qui n'est sous aucune licence.

Le rendu passe par `openscad-wasm-prebuilt` (OpenSCAD compilé en WebAssembly), sous
licence GPL-2.0-or-later : il n'est pas distribué avec le dépôt, `npm install` le télécharge
dans `node_modules/`. Les STL qu'il produit sont tirés des modèles de `../scad/` et suivent
leur licence (CERN-OHL-S-2.0, texte dans [`../LICENSES/`](../LICENSES/CERN-OHL-S-2.0.txt)) : la
GPL de l'outil ne les couvre pas. `generer_stl.mjs` écrit cette licence dans la ligne `solid` de
chaque STL.

`site.py` copie dans le site la police Mona Sans (`mona-sans.woff2`) et sa licence
(`mona-sans-OFL.txt`, SIL Open Font License 1.1) : la page la sert elle-même, sans passer par
Google Fonts. Le fichier de la police est celui du projet officiel, sans modification :
`fonts/webfonts/variable/MonaSansVF[opsz,wght].woff2` de l'archive `mona-sans-webfonts-v2.0.27.zip`
(version 2.0.27, <https://github.com/github/mona-sans/releases/tag/v2.0.27>), seulement renommé ;
`mona-sans-OFL.txt` est le `OFL.txt` de la même archive. Pour le mettre à jour, reprendre le même
fichier dans une version plus récente, sans le découper ni le convertir. Les mentions légales du pied de page (éditeur, hébergeur) sont dans `EDITEUR` et
`HEBERGEUR` en tête de `site.py` ; tant qu'un champ contient « à compléter », la fabrication du
site le signale.
