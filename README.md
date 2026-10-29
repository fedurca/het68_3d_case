# Kryt het68

Tisknutelný kryt akustického pole [het68](https://github.com/fedurca/het68). Krychle o hraně 384 mm stojí na vrcholu, mikrofon je ve středu každé stěny a kouká ven po její normále. Protilehlé membrány T5848 jsou od sebe 384 mm.

Core 160 × 100 mm a silová deska 140 × 80 mm z [het68_pcb v4.5.0](https://github.com/fedurca/het68_pcb/releases/tag/v4.5.0) leží ve středu detekční krychle, v kulové koruně. Koruna má v každém směru stejný poloměr, takže odraz od těla je všude stejný. Šest stopek je jeden díl a končí růžičkou s mikrofonem. Kabel od membrány k dutině měří **90 mm** v každém směru. Stonek dolů je stožár.

Koruna je slepená ze dvou polokoulí na O-kroužek, zvenku bez příruby. Stopka překrývá hrdlo zvonem, růžička překrývá stopku návlekem, víčko LED sedí v osazení. Dovnitř vede jen otvor T5848 s límcem na windscreen.

Firmware pro tuto mechaniku se překládá s `HET68_DOA_EDGE_MM=384`. Směry mikrofonů jsou `MIC_DIR` z [doa.c](https://github.com/fedurca/het68/blob/main/doa.c), návrh pole je v [array_cube_design.md](https://github.com/fedurca/het68/blob/main/array_cube_design.md). Starý kříž, fotka prototypu a naměřené míry jsou v [reference/GEOMETRY.md](reference/GEOMETRY.md).

Tělo je zelená ASA, ať sestava čte jako brokolice: kulová koruna, krátké stopky, růžičky ze tří srostlých kuliček. Víčko kruhu LED je přírodní průsvitná ASA a slouží jako difuzor, před mikrofon nepatří. Hladký úsek čepu DN 32 má stěnu 1,8 mm, koruna 8 mm. Tištěný čep do koruny má Ø31,7 × 28 mm, stonek mezi korunou a růžičkou má Ø44 mm. Stožár je skutečná trubka a do slepého hrdla se zasouvá 40 mm. Tištěné hrdlo má díru Ø32,4 mm.

## Sestava

Šest stejných stopek míří ve směru `MIC_DIR`. Mikrofon 1 je sever, elevace +35°. Šipka na jeho růžičce leží na horní straně a v sestavě ukazuje k severu. Šedá trubka je stonek, zasunutý 40 mm do slepého hrdla. Není to tištěný díl.

![Izometrie sestavy](export/img/assembly-iso.png)

![Bokorys sestavy](export/img/assembly-side.png)

![Půdorys sestavy](export/img/assembly-top.png)

Délka kabelu a hloubka zasunutí stožáru jsou v [export/CUT_LENGTHS.txt](export/CUT_LENGTHS.txt).

## Díly

Tištěné díly jsou v [export/stl](export/stl) a [export/step](export/step). Koruna je půlená v rovníku. Dutina je koule Ø204 mm, stoh 160 × 100 × 54 mm leží uprostřed. Zvenku je plášť koule Ø220 mm.

### Koruna, spodek

Tři dolní stopková hrdla a svislý stonek se slepým hrdlem HT DN 32. V rovníku je drážka na O-kroužek Ø2,5 mm. Čtyři sloupky se šroubem M3 jsou uvnitř, mimo desku.

![Spodní polokoule](export/img/hub_lower.png)

[hub_lower.stl](export/stl/hub_lower.stl) · [hub_lower.step](export/step/hub_lower.step)

### Koruna, vršek

Tři horní hrdla a jazýček, který zapadne do spodní dutiny. Vnější plocha navazuje na spodní polokouli bez příruby.

![Horní polokoule](export/img/hub_upper.png)

[hub_upper.stl](export/stl/hub_upper.stl) · [hub_upper.step](export/step/hub_upper.step)

### Stopka

Jeden díl pro všech šest směrů. Do koruny jde čep Ø31,7 × 28 mm, přes hrdlo je zvon. Mezi korunou a růžičkou je stonek Ø44 mm s dírou Ø28,4 mm, na konci límec Ø40 mm s jedním bajonetovým zubem. Žebro u čepu a zub jsou na stejné straně. Ta strana po nasazení míří k zemi, takže konektorová hrana satelitu je nejníž.

![Rameno](export/img/arm.png)

[arm.stl](export/stl/arm.stl) · [arm.step](export/step/arm.step)

### Růžička

Drží satelit 50 × 80 mm, světlost 56 × 86 mm. Tělo jsou tři srostlé kuličky seříznuté v rovině mikrofonu, ať růžička čte jako brokolice. Ven vede jen otvor T5848 a prstenec osmi SK6812, víčko LED se lepí do osazení. Návlek na tlustší stopce kryje bajonet. Nasazení je pootočené o 30° a dotočené tak, aby hrana s RJ45 byla dole.

![Růžička](export/img/pod.png)

[pod.stl](export/stl/pod.stl) · [pod.step](export/step/pod.step)

### Víčko LED

Průsvitný kroužek přes SK6812. Lem dosedne na čelo hlavice, krátký nákružek zapadne do prstence. Uprostřed zůstává díra a límec na pěnový windscreen.

![Víčko LED](export/img/pod_window.png)

[pod_window.stl](export/stl/pod_window.stl) · [pod_window.step](export/step/pod_window.step)

### Značka severu

Šipka pro druhou barvu, převýšení 0,8 mm. Soubor je ve stejném souřadném systému jako `pod.stl`, na horní stěně hlavice mikrofonu 1. V sestavě míří k severu.

![Značka severu](export/img/marks.png)

[marks.stl](export/stl/marks.stl) · [marks.step](export/step/marks.step)
