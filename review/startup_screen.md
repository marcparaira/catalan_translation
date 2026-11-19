# startup_screen translation: points for manual review

All of `startup_screen_l_english.yml` (287 entries, the historical introductions shown when you pick a country) is translated and merged into [ca_startup_screen_l_english.yml](../localisation/replace/ca_startup_screen_l_english.yml). **The Catalan shown is what the file contains now.** Write your decision in the last column (or tell me) and I'll apply it.

The conventions in [EU4.md](EU4.md) and [text.md](text.md) were followed; only new questions are listed here.

## 1. Decisions

1. **Errors in the English source: corrected.** All of these are now fixed in the Catalan text. They are also listed, with suggested English wording, in [paradox_errors/EU4_1.37.5_english_localisation.md](../paradox_errors/EU4_1.37.5_english_localisation.md).

   | Key | English says | Catalan now says |
   |---|---|---|
   | `string_start_aragon` | Alfons V is Joan's **father** | *al seu germà gran* |
   | `string_start_aragon` | almost no silk in Europe | silk made in València and Italy, eastern silk more prized |
   | `string_start_provence` | René **styles himself** King of Aragon; **duchy** of Provence | René *reclama el tron d'Aragó com a hereu de la seva mare, Violant d'Aragó*; *comtat* |
   | `string_start_scotland` | Alexander II | Alexandre III |
   | `string_start_ashikaga` | Yoshimasa is **the current Shogun** | *l'infant que encapçala la casa Ashikaga i futur xogun* |
   | `string_start_poland` | north-west | nord-est |
   | `string_start_austria` | Albert **fell in battle** | *va morir de disenteria … durant la campanya* |
   | `string_start_livonian_order` | 1237 | 1236 |
   | `string_start_mamluks_history` | coffee | removed |
   | `string_start_age_of_absolutism` | Aurangzeb | Jahangir |
   | `string_start_bavaria` | Erik | Cristòfol |
   | `string_start_milan` | Ludovico Sforza | Francesco Sforza |
   | `string_start_bohemia` | moderate Taborites | *utraquistes* |
   | `string_start_tag_arabia` | caliph as "prophet" | *successor del Profeta* |

   Not changed: `string_start_eastern_japan`. The English describes the Kamakura kubo office in general terms and never says it was filled in 1444.

2. **Start-screen titles without an article.** «[GovernmentName] [GetCaDe] [GetName], 1444» (*Regne de França, 1444*) avoids the unknown gender of the government name. The plural variant «[GovernmentName] [GetAdjective]» still uses the masculine adjective (*República veneciana* would come out as *República venecià*).
3. **Native American peoples** keep the game's form, lowercase and invariable (*els kiche*, *els pawnee*, *els mohawk*), except those with an established Catalan form (*iroquesos*, *hurons*, *cherokees*, *nahues*, *quítxues*).
4. **Continents** have no article helper: «Esteu jugant a Amèrica del Nord» (should be *a l'Amèrica del Nord*).

## 2. Terms coined in this file (proposed glossary additions)

| English | Catalan used |
|---|---|
| Arch-King | arxirei (like *arxiduc*) |
| Voivode | voivoda, pl. voivodes |
| High King (Ireland) | gran rei |
| Suzerain | senyor suprem |
| Chiefdom / Mound builders | cacicat / constructors de túmuls |
| Government Interactions | interaccions de govern |
| Native Council / Native Advancements | consell indígena / avenços indígenes |
| Blessings, Rituals, Personal Deity, Cult, Aspects of Faith, State Church, Faith Power, Doomsday, Harmony | benediccions, rituals, deïtat personal, culte, aspectes de la fe, Església d'Estat, poder de la fe, fi del món, harmonia |
| Religion groups | grup religiós dhàrmic / oriental / cristià / musulmà |
| Shah (in names) | Xah (Xah Rukh, Jahan Xah, Bahman Xah) |
| Dynasties | nassarites, marínides, hàfsides, aiúbides, timúrides, Comnens, Trastàmara, Mèdici |
| Peoples | chankes, chichimeces, purépecha, tais, ioruba |

## 3. Changes I made for consistency after merging

Applied across all Catalan files:

- **Arch-King** → **arxirei** everywhere (one chunk had *arquirei*).
- **xògun** → **xogun** (2 entries), matching the other 30.
- **Opríxnina** → **Opritxnina** (`opprichnina` in powers_and_ideas), matching the EU4 button.
- **L'Ovella Negra** → **Els Xais Negres** (`qar_black_sheep` and its description), to pair with the existing *Els Xais Blancs*.
- **mar Bàltic / mar Negre** → **la mar Bàltica / la mar Negra** (8 entries, with their articles), matching the sea-zone names in `provincies.tsv`.
- **khan(s)** as a common noun → **kan(s)** (about 14 entries, including *Kan dels Kans* and *il-kans*), matching the ruler titles. *Khan* inside personal names (*Genguis Khan*, *Kublai Khan*) is unchanged.
- **chanques** → **chankes**.

## 4. Entry-by-entry list

| Key | English | Catalan (current) | Issue / alternatives | Decision |
|---|---|---|---|---|
| `string_screen_title_plural` | The [Root.GetAdjective] [Root.GovernmentName] | [Root.GovernmentName] [Root.GetAdjective] | Masculine adjective (§1.5): fine for Regne/Imperi/Soldanat, wrong if GovernmentName is feminine (República, Teocràcia). Article dropped from both screen titles to avoid el/la agreement with GovernmentName. |  |
| `string_start_title_monarchy_plural` | The [Dynasty] [GovernmentName] | [Root.GovernmentName] de la dinastia [Dynasty] | Reworded to avoid «Imperi Osman»-style apposition and gender agreement; Spanish uses «El [Gov] [Dyn]». |  |
| `string_start_title_native_council` | The [Root.GetName] Tribes | Les tribus [Root.GetCaDe] [Root.GetName] | Wanted «Les tribus [GetCaAdjFP]» (hurones…), but the validator requires [Root.GetName]. |  |
| `string_start_title_denmark` | Cristopher, the Arch-King of Denmark | Cristòfol, arquirei de Dinamarca | «arquirei» coined for archirex/Arch-King; alternative «rei suprem». | Changed to *arxirei* (§3) |
| `string_start_title_trebizond` | The Komnenoi | Els Comnens | Catalan plural of Comnè; alternative «els Comnè» (invariable). |  |
| `string_start_maghreb` | The §YHasfids§! of Tunis | Els §Yhàfsides§! de Tunis | Source typo (Hasfids → Hafsids) silently corrected. Dynasties: nassarites, zayyànides, marínides, wattàssides, hàfsides, rustàmides. |  |
| `string_start_provence` | The Duchy of Provence itself… King of Aragon | El ducat de Provença… rei d'Aragó | Historical: Provence was a county, not a duchy; René only claimed Aragon from 1466. Translated as in source. |  |
| `string_start_scotland` | The Hebrides were wrested… under Alexander II | sota Alexandre II | Historical: the Hebrides were gained under Alexander III (Largs 1263, Treaty of Perth 1266). Translated as in source. |  |
| `string_start_eastern_japan` | the Kamakura Kubo | el kubo de Kamakura | Historical: in 1444 the Kamakura kubo office was vacant (after the Eikyō rebellion, restored 1449); also Yoshimasa only became shogun in 1449 (`string_start_ashikaga`). Translated as in source. |  |
| `string_start_irish_minors` | the §YPale§! / High King | el §YPale§! / gran rei | «Pale» kept as in province PROV373 (masc. «el Pale»); High King (Ard Rí) = «gran rei». Earldoms/earls → comtats/comtes. |  |
| `string_start_romania` | Voivode / §YStefan§! / §YIlias I§! / Vlad Dracula | voivoda / §YEsteve§! / §YIlias I§! / Vlad Dràcula | «voivoda» (pl. voivodes) coined here, will recur. Stefan → Esteve (Catalan Wikipedia «Esteve II de Moldàvia»); Ilias kept. |  |
| `string_start_ashikaga` | Shogun / Daimyo / Kanrei / Kamakura office | xogun, xogunat / daimyo (invariable) / kanrei / seu de Kamakura | Follows existing ca_ files (xogun, kubo, «Seu de Kamakura»). |  |
| `string_start_mutapa` | §YMwenemutapa§!, that is, 'the Lords of the Land' | els §YMwenemutapa§!, és a dir, «els senyors de la terra» | Mwenemutapa is really a royal title (sing.), usually glossed «lord of the conquered lands». Kept source meaning. |  |
| `string_start_aztecs` | Purépecha / Chichimeca / Tolluca / Mexico-Tenochtilan | purépecha (invariable) / chichimeces / Toluca / Mèxic-Tenochtitlan | Adjective forms from paisos (TAR, CCM); source typos Tolluca/Tenochtilan corrected; Michoacán, Pátzcuaro, Tariácuri with accents. |  |
| `string_start_ethiopia` | Sword of Islam / Further down the Nile | l'Espasa de l'islam / A la vall del Nil | «Further down the Nile» is geographically odd (Nubia is downstream = north); rendered neutrally. |  |
| `string_start_aragon` | Should King Joan manage to survive his father Alfons V | Si el §Yrei Joan§! aconsegueix sobreviure al seu pare, §YAlfons V§! | Historical error in source: Alfons V was Joan II's elder brother, not his father. Translated faithfully; recommend «al seu germà». |  |
| `string_start_aragon` | Silk has traditionally seen almost no production in Europe | Tradicionalment, a Europa amb prou feines se n'ha produït | Dubious claim: silk was produced in Valencia, Italy and Byzantium well before 1444. Kept as in source. |  |
| `string_start_denmark`, `string_start_gotland` | first Arch-King of the North / Arch-King of Denmark | primer arxirei del Nord / §Yarxirei de Dinamarca§! | Coined «arxirei» (like arxiduc) for the ARCHKING title; alternatives «arquirei» or «rei suprem». Must match ARCHKING and the Danish decisions when those are translated. |  |
| `string_start_poland` | the Russian Principalities, lead by Muscovy in the north west | encapçalats per §YMoscòvia§! al nord-oest | Geographic error in source: Muscovy lies north-east of Poland-Lithuania (the same text later says «far north east»). Kept faithfully; recommend «nord-est». |  |
| `string_start_austria` | Albert fell in battle against the Turks in 1439 | Albert va caure en combat contra els turcs el 1439 | Historical error: Albert II died of dysentery during the campaign, not in battle. Kept; could soften to «va morir durant la campanya contra els turcs». |  |
| `string_start_livonian_order` | suffered a heavy defeat against the Lithuanians in 1237 | van patir una greu derrota davant els lituans el 1237 | The battle of Saule was in 1236 (the merger into the Teutonic Order was 1237). Kept 1237. |  |
| `string_start_mamluks_history` | vessels ... with coffee, cloth and spices through the Red Sea | carregats de cafè, teixits i espècies | Anachronism: the Red Sea coffee trade only starts c. 1500. Kept. |  |
| `strong_start_mayans` (also iroquois, huron, plains, osage, cherokee…) | §YKiche§! people, §YKaqchikel§!, §YXiu§!, Pawnee, Mohawk… | el poble §Ykiche§!, els §Ykaqchikel§!, els §Yxiu§!, els pawnee, els mohawk | Native ethnonyms kept in the game's form, lowercase and invariable (paisos.tsv forms), rather than Catalan adaptations (quitxés, cakxiquels, mohawks). Exceptions with established Catalan forms: iroquesos, hurons, cherokees, olmeca, huasteca, nahues, quítxues. Recurring choice for native texts. |  |
| `string_start_cusco` | §YChanka Wars§! / 'Ground Shaker' | §Yguerres contra els chankes§! / «el que sacseja la terra» | No established Catalan name for the Chanka war; plural «chankes» coined. Alternative: «guerra chanka». |  |
| `string_start_cherokee`, `string_start_creek` | Coosa chiefdom / Mound builders | cacicat de Coosa / constructors de túmuls | «cacicat» for native chiefdom (already used elsewhere in ca_*); «constructors de túmuls» matches existing texts. Proposed for glossary. |  |
| `string_start_age_of_absolutism` | Akbar the Great has just left a thriving and expansionist Mughal Empire to his son Aurangzeb | Akbar el Gran acaba de deixar al seu fill Aurangzeb un Imperi Mogol pròsper | Historical error in source: Akbar's son and successor was Jahangir (1605); Aurangzeb was his great-grandson (r. 1658–1707). Translated faithfully; could silently correct to «Jahangir» or «als seus successors». |  |
| `string_start_aq_qoyunlu` | the Aq Qoyunlu, or White Sheep … the Qara Qoyunlu, the Black Sheep | els Aq Qoyunlu, o Xais Blancs … els Qara Qoyunlu, o Xais Negres | Followed existing `akk_white_sheep` «Els Xais Blancs»; but existing `qar_black_sheep` says «L'Ovella Negra». Same in `string_start_qara_qoyunlu`. Pick one (Xais Blancs/Negres vs Ovella Blanca/Negra) and align. | Harmonised to *Xais Negres* (§3) |
| `string_start_timurids` | Timur … Shah Rukh … Jahân Shâh … Bahman Shah | Tamerlà … Xah Rukh … Jahan Xah … Bahman Xah | Timur → Tamerlà (as in existing text); «Shah» inside personal names → «Xah» (Xah Rukh, Jahan Xah, Ala-ud-Din Hasan Bahman Xah, Mahmud Xah, Muhammad Xah II), following existing usage; dynasty name «Ilyas Shahi» kept as in the game. Other names kept in game form (Muhammad bin Baysonqor, Ulugh Beg, Gawhar Shad, Bayandor Khan, Oghuz Kagan). |  |
| `string_start_religion_mechanic_title` | [Root.GetName] is [Root.Religion.GetName] | Religió [Root.GetCaDe] [Root.GetName]: [Root.Religion.GetName] | Religion names mix adjectives (catòlica) and nouns (xintoisme), so «X és xintoisme» fails; rephrased as label. Same for `_plural` and `string_start_religion_intro_text` («La vostra religió (§Y…§!) dona els modificadors següents»). |  |
| `string_start_tag_europe` | lead the [Root.GetAdjective] [Root.GovernmentName] through this period | guiar el poble [Root.GetAdjective] i el seu govern ([Root.GovernmentName]) | GovernmentName gender unknown (Regne/República) and GetAdjective is masculine, so the adjective now agrees with «poble». `string_start_tag_generic` uses «com a [Root.GovernmentName], §Y[Root.GetName]§! és un país…». |  |
| `string_blessings_info` | Blessings / Rituals / Personal Deity / Cult / Aspects of Faith / State Church / Faith Power / Torah Aspects / Ancestor / Doomsday / Harmony | benediccions / rituals / deïtat personal / culte / aspectes de la fe / Església d'Estat / poder de la fe / aspectes de la Torà / avantpassat / fi del món / harmonia, harmonitzar | Coined religion-mechanic terms not yet in any ca_ file (they recur in religion/DLC files). Doomsday = «fi del món» follows existing doom tooltips; «aspectes de la fe» vs existing «aspecte de l'Església» (ADD_CHURCH_ASPECT_EFFECT). Fervor foci rendered «centrar el país en la guerra/comerç/estabilitat». Dharmic group = «dhàrmic». |  |
| `string_stories_info` | Fetishist rulers can select a Cult … countries starting with the Alcheringa faith | Els governants fetitxistes poden triar un culte … la fe alcheringa | Source says «Fetishist» in the Alcheringa text (copy of cults_info); kept as source. Could read «Els governants alcheringa». |  |
| `string_start_tag_north_india` | Founded in the 13th Century as a Shan Mong … the Paik system | Fundat al segle XIII com un mong xan … el sistema paik | «Mong» (Shan principality) left as a common noun «mong xan»; alternative «principat xan». Other coined forms here: sayyids, khaljis, balutxi Langa, gonds/vindhyans, Katmandú. |  |
| `string_start_tag_south_america` | the young prince Yupanki Pachacutec … the neighboring Chancas | el jove príncep Yupanki Pachacútec … els veïns chanques | Accent added (Pachacútec, as in existing text); Chanca people adapted as «chanques». Alternative: keep «chancas». | *chanques* → *chankes* (§3) |
| `string_start_bavaria` | Denmark too is ruled by a Wittelsbach king, Erik, the Arch-King of the North | Dinamarca també la governa un rei Wittelsbach, Eric, l'arxirei del Nord | Source error: in 1444 the Wittelsbach king of Denmark is Christopher of Bavaria (Cristòfor III); Erik of Pomerania was deposed in 1439. Kept «Eric»; alternative: correct to «Cristòfor». «Arxirei del Nord» coined for *Arch-King*. |  |
| `string_start_milan` | the ambitious and highly skilled mercenary captain Ludovico Sforza | el capità mercenari Ludovico Sforza | Source error: the condottiere in 1444 is Francesco Sforza (Francesc Sforza); Ludovico was born in 1452. Kept the source name. |  |
| `string_start_bohemia` | the moderate Taborite faction, led by Jiri Podebrad | la facció moderada dels utraquistes, encapçalada per Jordi de Podebrady | Source error (Taborites were the radical faction; Poděbrady led the moderate Utraquists), corrected to «utraquistes». «Poděbrady» written without ě (not in Windows-1252). |  |
| `string_start_tag_arabia` | the title of Caliph, leader and prophet of all Islam | el títol de califa, successor del Profeta i guia de tot l'islam | Source error: a caliph is not a prophet. Rewritten as «successor del Profeta». Literal alternative: «líder i profeta». |  |
| `string_start_government_monarchy` | [Root.GovernmentName]s are Monarchies. | El vostre estat ([Root.GovernmentName]) és una monarquia. | GovernmentName (Regne, Ducat, República…) can't be pluralised and its gender is unknown. Same pattern in `_monarchy_regency`, `_theocracy`, `_papacy` and `string_tribal_reform` («El nostre estat (…) té una forma de govern tribal»). |  |
| `string_start_culture_government_title` | [Root.Culture.GetName] [Root.GovernmentName] | [Root.GovernmentName] de cultura [Root.Culture.GetName] | Avoids adjective agreement (culture names are feminine adjectives, government names can be masculine): «Regne de cultura francesa». Same in `_plural`. |  |
| `string_start_religion_fallback` | The [Religion.GetName] faith belongs to the [GetGroupName] Group | La vostra fe ([Root.Religion.GetName]) pertany al grup de fe [Root.Religion.GetGroupName] | Group names are feminine adjectives (musulmana, oriental), so «grup de fe musulmana»; religion names mix nouns and adjectives, so they go in parentheses. Same in `string_start_religion_norse`. |  |
| `string_start_government_native_councils_plural` | The [Root.GetName] are a Native Tribe | [Root.GetName]: som una tribu indígena | Plural country names: verb agreement unknown, so a colon is used. The singular key uses «[GetCaElCap] [GetName] és una tribu indígena». |  |
| `string_start_russian_mechanics` | Reforming Sudebnik / Supporting the Oprichnina / Raising Streltsy | Reformar el Sudébnik / Donar suport a l'Opritxnina / Equipar els strelsí | Uses the in-game button labels (RUSABIL_*), not the English wording. Existing files disagree: `RUSABIL_OPRICHNINA` has «Opritxnina» but `opprichnina` has «Opríxnina». Used «Opritxnina». | Harmonised to *Opritxnina* (§3) |
| `string_start_mamluks` | Government Interactions: Promote Ruler Culture / Sell Slaves of Ruler's Culture / Recruiting from Ruler's Culture | interaccions de govern: Promoure la cultura del governant / Vendre esclaus… / Reclutar entre la cultura del governant | Coined «interaccions de govern» (recurs in iqta, tribal federation, feudal theocracy, shogunate). The Mamluk interaction labels aren't translated anywhere yet, so check them against those keys when they are. |  |
| `string_start_native_council` | Native Council / Native Advancements / Reform our Society | consell indígena / avenços indígenes / reformar la nostra societat | Coined; these labels aren't in the merged files yet. Also «consell indígena siberià» in `string_start_siberian_native_council_opm`. |  |
| `string_start_dutch_minors` | The Low Countries … perhaps even unifying the Netherlands | Els Països Baixos … fins a unificar els Països Baixos | «Low Countries» and «Netherlands» (NED) are both «Països Baixos» in Catalan. The final clause reads slightly redundantly. |  |
| `string_start_no_special_region_title` | You are playing in [Root.capital_continent_title]: | Esteu jugant a [Root.capital_continent_title]: | Continent names have no article helper, so it gives «a Amèrica del Nord» (normally «a l'Amèrica del Nord»). Same in `string_start_africa_americas_description` («Amèrica del Nord comença…»). |  |
