# Guia d'estil

Normes per a la traducció catalana d'EU4. Si un cas no hi és, seguiu l'[Optimot](https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html) i la normativa de l'IEC. La terminologia és a [glossari.md](glossari.md).

## 1. Abast

- **Joc base només** (v1.37.5.0, totes les DLC). No es tradueixen mods de tercers.
- Es tradueix **tot el text dels fitxers de localització**, inclosos els noms de països, províncies, àrees, regions i adjectius.
- **No es pot traduir** des d'un mod de localització: els noms de monarques, generals i dinasties (són a `history/` i `common/`) ni els noms de província per cultura (`common/province_names/`), que substitueixen el nom traduït quan la província és d'una altra cultura.

## 2. Llengua i registre

- **Català central normatiu**, registre formal però àgil, sense arcaismes forçats.
- **El jugador**: segona persona del plural (*Podeu declarar la guerra…*, *Esteu segur?*). Serveix tant per al *vós* com per al *vosaltres*.
- **La nació en primera persona**, com fa l'anglès (*Our nation* → *La nostra nació*, *We* → *Nosaltres*).
- **El monarca**: *Majestat* (*Your Majesty* → *Majestat* / *Vostra Majestat*).
- **Les frases** han de sonar naturals. Es pot reordenar, partir o ajuntar frases sempre que es conservi el sentit i tots els codis.

## 3. Majúscules

En català la majúscula és molt menys freqüent que en anglès:

| Cas | Norma | Exemple |
|---|---|---|
| Termes de joc dins una frase | minúscula | *Guanyeu 10 de §Yprestigi§!* (no *Prestigi*) |
| Etiquetes, títols de finestra, botons | majúscula inicial només | *Esgotament bèl·lic*, *Reforma de govern* |
| Èpoques, institucions, períodes històrics | majúscula | *el Renaixement*, *la Il·lustració*, *l'Era dels Descobriments* |
| Entitats polítiques i institucions concretes | majúscula | *el Sacre Imperi Romanogermànic*, *la Cúria*, *la Lliga Hanseàtica* |
| Gentilicis i adjectius de país | minúscula | *exèrcit anglès*, *idees castellanes* |
| Religions (nom de la religió) | minúscula | *catòlica*, *sunnita*, *xintoisme* |
| Títols nobiliaris | minúscula (dins frase) | *el rei de França*, *l'emperador* |

## 4. Ortotipografia

- **Apòstrof**: recte `'` (no `’`), com a l'original anglès.
- **Ela geminada**: amb punt volat `l·l` (U+00B7), mai amb punt baix (`l.l`) ni `l•l`.
- **Cometes**: llatines `« »` per a citacions dins del text; si cal un segon nivell, `" "`. No feu servir `“ ”`.
- **Guió llarg** `—` per a incisos i diàlegs.
- **Punts suspensius**: tres punts `...`, com l'original.
- **Xifres i percentatges**: es mantenen com els escriu el joc (`10%`, `1.5`), perquè els números que insereix el motor surten en format anglès i cal coherència.
- **Dates**: *1 de gener de 1444* (mesos en minúscula). El format de data del motor es tradueix a les claus corresponents.
- **Caràcters**: només els del joc de caràcters Windows-1252. Tots els accents catalans hi són; símbols com ✓ o → no es veuen al joc (el validador ho comprova).

## 5. Codis del joc (obligatori)

El validador (`tools/catloc.py validate`) rebutja qualsevol entrada que no els conservi exactament:

| Codi | Exemple | Norma |
|---|---|---|
| Variables | `$WHO$`, `$NAME\|Y$` | Idèntiques, incloent-hi `\|Y` |
| Àmbits | `[Root.GetName]` | Idèntics (excepte els ajudants `GetCa…` del §6) |
| Colors | `§Y…§!` | Mateixos colors i mateix nombre de `§!`; envolten la paraula traduïda equivalent |
| Icones | `£adm£` | Idèntiques |
| Banderes | `@SWE` | Idèntiques |
| Salts de línia | `\n` | Mateix nombre (avís, no error) |

Els codis es poden **moure** dins la frase. La versió numèrica (`:0`, `:1`) la posen les eines; no la toqueu.

## 6. Noms inserits dinàmicament

L'anglès insereix noms en frases fetes (`the army of [Root.GetName]`). En català això trenca les contraccions (*de el Japó*, *de Anglaterra*). Fem servir **ajudants propis** (`customizable_localization`) que trien la forma correcta segons el país, com fa la traducció francesa oficial.

### Ajudants (pendents d'implementar; vegeu §9)

Àmbit de país (`Root`, `From`, `Owner`, `Overlord`…):

| Ajudant | Retorna | Ús |
|---|---|---|
| `GetCaEl` / `GetCaElCap` | *(res)*, el, la, l', els, les | `[Root.GetCaEl] [Root.GetName]` → *França*, *el Japó*, *l'Índia* |
| `GetCaDe` / `GetCaDeCap` | de, d', del, de la, de l', dels, de les | `[Root.GetCaDe] [Root.GetName]` → *de França*, *d'Anglaterra*, *del Japó* |
| `GetCaA` / `GetCaACap` | a, al, a la, a l', als, a les | `[Root.GetCaA] [Root.GetName]` → *a França*, *al Japó* |
| `GetCaPer` / `GetCaPerCap` | per, pel, per la, per l', pels, per les | `[Root.GetCaPer] [Root.GetName]` |
| `GetCaAdjFS` / `GetCaAdjMP` / `GetCaAdjFP` | adjectiu femení / masc. plural / fem. plural | `l'armada [Root.GetCaAdjFS]` → *l'armada anglesa* |

`GetAdjective` (sense ajudant) dona el **masculí singular**: *l'exèrcit [Root.GetAdjective]* → *l'exèrcit anglès*.

Àmbit de província:

| Ajudant | Retorna | Ús |
|---|---|---|
| `GetCaDeProv` / `GetCaDeProvCap` | de, d' | `[Root.GetCaDeProv] [Root.GetName]` → *de Barcelona*, *d'Amsterdam* |

Sempre amb **un espai** entre l'ajudant i el nom: els valors elidits (`d'`, `l'`) acaben en `£`, que fa desaparèixer l'espai que ve després.

### Quan el nom ve en una variable (`$COUNTRY$`, `$PROVINCE$`…)

No hi ha ajudant possible. Reformuleu-ho per no posar *de/a/el* just davant:

- *The armies of $COUNTRY$* → *Els exèrcits de $COUNTRY$* és acceptable si el nom rarament comença per vocal; si no, reformuleu-ho: *$COUNTRY$: exèrcits* o *Exèrcits del país ($COUNTRY$)*. Feu servir el sentit comú: més val una frase una mica menys elegant que una errada visible.

### Gènere del governant

Eviteu els adjectius que concorden amb el governant (*savi/sàvia*): reformuleu-ho amb substantius (*té saviesa*) o amb termes epicens (*governant*, *monarca*, *consort*). Si en un cas concret no es pot evitar, s'afegirà un ajudant específic.

## 7. Noms propis

### Països, províncies, àrees i regions

1. **Exònim català establert** si n'hi ha (Viquipèdia en català, Gran Enciclopèdia Catalana, *Nomenclàtor mundial* de l'IEC): *Anglaterra*, *Castella*, *Aragó*, *Nàpols*, *Moscòvia*, *Saragossa*, *Estocolm*, *Lisboa*, *Constantinoble*.
2. Si no n'hi ha, **es manté la forma del joc** tal com és, sense inventar transliteracions: *Qara Qoyunlu*, *Majapahit*, *Gujarat*.
3. **Sense article al nom.** L'article (*el Japó*, *la Xina*, *els Països Baixos*) l'afegeixen els ajudants del §6; per això `JAP` es tradueix *Japó*, no *el Japó*.
4. Els noms de país en plural de l'anglès (*Ottomans*, *Mamluks*, *Timurids*) es tradueixen pel nom de l'estat: *Imperi Otomà*, *Soldanat Mameluc*, *Imperi Timúrida*.
5. Les províncies conserven el topònim històric que fa servir el joc si és diferent de l'actual (*Constantinoble*, no *Istanbul*, si el joc diu *Constantinople*).

### Persones històriques citades en el text

Forma catalana si és establerta (*Carles V*, *Felip II*, *Lluís XIV*, *Solimà el Magnífic*, *Isabel I de Castella*, *Ferran el Catòlic*); si no, la forma original.

## 8. Llargada i abreviatures

- Els textos d'interfície tenen l'espai limitat i el català és un 15–20% més llarg. Les etiquetes curtes de l'anglès s'han de mantenir curtes.
- Si cal abreujar: **ADM**, **DIP**, **MIL** (poders); *Desenv.* (desenvolupament); *Màx.*; *Mín.*; *Mod.* (modificador). Sempre amb punt quan la paraula queda tallada.
- Si un text desborda al joc, s'anota i s'escurça.

## 9. Pendent abans de la fase 3

1. Crear la taula de països i províncies (`glossary/paisos.tsv`, `glossary/provincies.tsv`) amb el nom, l'article i les quatre formes de l'adjectiu.
2. Generar-ne el fitxer `customizable_localization/` amb els ajudants del §6.
3. Comprovar al joc que el truc `d'£` també funciona amb el joc en anglès.
