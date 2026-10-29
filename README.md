# Kryt het68

Tisknutelný kryt akustického pole [het68](https://github.com/fedurca/het68). Krychle o hraně 384 mm stojí na vrcholu, mikrofon je ve středu každé stěny a kouká ven po její normále. Protilehlé membrány T5848 jsou od sebe 384 mm. Střed pole je malý rozbočovač HT DN 32. Desky z [het68_pcb v4.5.0](https://github.com/fedurca/het68_pcb/releases/tag/v4.5.0) jsou ve skříni pod dolním vrcholem, mimo akustický objem.

Firmware pro tuto mechaniku se překládá s `HET68_DOA_EDGE_MM=384`. Směry mikrofonů jsou `MIC_DIR` z [doa.c](https://github.com/fedurca/het68/blob/main/doa.c), návrh pole je v [array_cube_design.md](https://github.com/fedurca/het68/blob/main/array_cube_design.md). Starý kříž, fotka prototypu a naměřené míry jsou v [reference/GEOMETRY.md](reference/GEOMETRY.md).

Tělo je zelená ASA. Víčko kruhu LED je přírodní průsvitná ASA a slouží jako difuzor, před mikrofon nepatří. Hladký úsek DN 32 má stěnu 1,8 mm, skříň a hlavice 3 mm. Tištěný čep má Ø31,7 × 40 mm, aby vlezl do skutečného hrdla. Tištěné hrdlo má díru Ø32,4 mm, aby do něj vlezla trubka Ø32 mm.

## Sestava

Šest ramen míří ve směru `MIC_DIR`. Mikrofon 1 je sever, elevace +35°. Šipka na jeho hlavici leží na horní stěně a v sestavě ukazuje k severu. Svislá trubka mezi rozbočovačem a skříní je skladová HT DN 32.

![Izometrie sestavy](export/img/assembly-iso.png)

![Bokorys sestavy](export/img/assembly-side.png)

![Půdorys sestavy](export/img/assembly-top.png)

Řez páteřní trubky mezi sedlem rozbočovače a sedlem víka je **249 mm**. Do každého hrdla se zasouvá 40 mm. Text je v [export/CUT_LENGTHS.txt](export/CUT_LENGTHS.txt).

## Díly

Tištěné díly jsou v [export/stl](export/stl) a [export/step](export/step).

### Rozbočovač

Šest hrdel DN 32 ve směru mikrofonů a sedmé svisle dolů na páteř. Dutina uprostřed svede jen kabely. Drážka v hrdle natočí žebro tištěného ramene, hladká trubka hrdlem projde taky.

![Rozbočovač](export/img/hub.png)

[hub.stl](export/stl/hub.stl) · [hub.step](export/step/hub.step)

### Rameno

Čep Ø31,7 × 40 mm, nákružek jako doraz, hladká trubka DN 32 a límec s jedním bajonetovým zubem. Žebro u čepu a zub jsou na stejné straně. Ta strana po nasazení míří k zemi, takže konektorová hrana satelitu je nejníž.

![Rameno](export/img/arm.png)

[arm.stl](export/stl/arm.stl) · [arm.step](export/step/arm.step)

### Hlavice

Drží satelit 50 × 80 mm, světlost 56 × 86 mm. Ven vede jen otvor T5848 a prstenec osmi SK6812. Deska se zasouvá od rozbočovače a dosedne na vnitřní stranu čela. Bajonet má jednu drážku: nasazení pootočené o 30° a dotočení do polohy, kde je hrana s RJ45 dole.

![Hlavice satelitu](export/img/pod.png)

[pod.stl](export/stl/pod.stl) · [pod.step](export/step/pod.step)

### Víčko LED

Průsvitný kroužek přes SK6812. Lem dosedne na čelo hlavice, krátký nákružek zapadne do prstence. Uprostřed zůstává díra a límec na pěnový windscreen.

![Víčko LED](export/img/pod_window.png)

[pod_window.stl](export/stl/pod_window.stl) · [pod_window.step](export/step/pod_window.step)

### Skříň

Spodní půlka. Světlost pojme stoh 160 × 100 × 54 mm, tedy Core 160 × 100 mm a silovou desku 140 × 80 mm s držákem 21700. Lišty vedou desku z boku. Nahoře je příruba s drážkou na O-kroužek Ø2,5 mm a čtyřmi dírami M3. Pod dnem je hrdlo stožáru DN 32, kabely jdou dál dírou Ø18 mm.

![Skříň elektroniky](export/img/electronics_box.png)

[electronics_box.stl](export/stl/electronics_box.stl) · [electronics_box.step](export/step/electronics_box.step)

### Víko skříně

Horní půlka s přírubou, čtyřmi dírami M3 a lemem do světlosti skříně. Nahoru ční hrdlo páteřní trubky. Tyč nestojí v ose žádného mikrofonu.

![Víko skříně](export/img/electronics_lid.png)

[electronics_lid.stl](export/stl/electronics_lid.stl) · [electronics_lid.step](export/step/electronics_lid.step)

### Značka severu

Šipka pro druhou barvu, převýšení 0,8 mm. Soubor je ve stejném souřadném systému jako `pod.stl`, na horní stěně hlavice mikrofonu 1. V sestavě míří k severu.

![Značka severu](export/img/marks.png)

[marks.stl](export/stl/marks.stl) · [marks.step](export/step/marks.step)
