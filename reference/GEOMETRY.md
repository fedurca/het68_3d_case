# Podklady geometrie het68

Mechanický kryt navazuje na tyto vstupy. Čísla níže jsou naměřená z STL nebo převzatá z firmware a z desek `het68_pcb` v4.5.0.

## Prototyp a starý model

Fotka [`img/prototyp.jpg`](img/prototyp.jpg) je první sestava: černý HT kříž na šedém stožáru, elektronika přichycená vně trubky.

| Soubor | Co to je |
|---|---|
| [`stl/spojka.stl`](stl/spojka.stl) | Šestiramenný rozbočovač, obálka 120 × 120 × 120 mm, střed v počátku |
| [`stl/vicko.stl`](stl/vicko.stl) | Víčko exportované v poloze z=13…29 mm, vnější Ø35 mm |
| [`img/spojka-iso.jpg`](img/spojka-iso.jpg) | Izometrie spojky |
| [`img/spojka-vykres.jpg`](img/spojka-vykres.jpg) | Výkres Ø42 / Ø33,2. Pro stavbu neplatí |
| [`img/spojka-rez.jpg`](img/spojka-rez.jpg) | Řez spojkou |
| [`img/vicko-iso.jpg`](img/vicko-iso.jpg) | Izometrie víčka |
| [`img/vicko-pohled.jpg`](img/vicko-pohled.jpg) | Pohled na víčko |

Naměřená spojka (řez sítí): ramena vnější Ø32 mm, díra Ø28 mm, stěna 2 mm, ústí bez drážky a bez bajonetu. Víčko má lem Ø33,1 mm a na díru Ø28 nesedí. Výkres Ø42 / Ø33,2 se nepoužívá.

Platí odpadní HT DN 32 podle ČSN EN 1451-1: vnější průměr trubky 32 mm, stěna 1,8 mm, díra 28,4 mm, hloubka hrdla 40 mm, vnější průměr lisovaného hrdla 44 mm.

## Pole mikrofonů

Geometrie, na kterou počítá DOA, je v [array_cube_design.md](https://github.com/fedurca/het68/blob/main/array_cube_design.md) a ve vektorech `MIC_DIR` v [`doa.c`](https://github.com/fedurca/het68/blob/main/doa.c).

Krychle stojí na vrcholu, tělesová úhlopříčka je svisle. Mikrofon je ve středu každé stěny a kouká ven po normále. Protilehlé stěny dělí hrana krychle. Sweet spot je **384 mm**. Střed stěny je 192 mm od středu pole. Sousední základna je 384 / √2 = 271 mm. Dolní vrchol je 384 × √3 / 2 = 333 mm pod středem.

```
MIC_DIR (jednotkové, pořadí USB 1…6)
1  +0.81650  0.00000  +0.57735   sever, +35,26°
2  -0.40825  +0.70711  +0.57735   azimut 120°, +35,26°
3  -0.40825  -0.70711  +0.57735   azimut 240°, +35,26°
4  -0.81650  0.00000  -0.57735   proti 1
5  +0.40825  -0.70711  -0.57735   proti 2
6  +0.40825  +0.70711  -0.57735   proti 3
```

`doa.c` na větvi main bez přepínače používá hranu 128 mm (`DOA_EDGE_MM`). Release workflow firmwaru sestavuje s `HET68_DOA_EDGE_MM=128`. Tento kryt je na 384 mm, firmware se má překládat `HET68_DOA_EDGE_MM=384`.

Starý kříž na fotce má jedno rameno svisle a stožár v dolním portu. To s `MIC_DIR` nesedí. Šest stopek a růžiček je jeden díl. Plášť tisknutelného krytu je koule, takže odraz je stejný v každém směru.

## Tisknutelný kryt

Koruna je koule Ø220 mm, dutina Ø204 mm, řez v rovníku bez vnější příruby. Do dutiny se vejde Core 160 × 100 mm a silová deska 140 × 80 mm z het68_pcb v4.6.0, obě se středem v počátku. Silová deska je v rovině z = −2 mm, článek Keystone 1122 (výška 23 mm) míří dolů. Core je v rovině z = 8 mm, šest RJ45 (výška těla 13,6 mm) míří nahoru. Největší roh této obálky je uvnitř dutiny.

Sloupky ve spodní půlce sedí na dírách desek. Silová deska: (±66, ±36) mm. Core: (−75,05, 20,95), (−74, 44), (74, −44), (74, 44) mm. Díry Core jsou mimo obrys silové desky, takže sloupek ke Core jde vedle ní.

Stopka je jeden díl. Čep Ø31,7 × 28 mm vleze do tištěného hrdla Ø32,4 mm, žebro do drážky. Stonek má Ø44 mm a díru Ø28,4 mm. Zástrčka RJ45 má průřez 11,7 × 8 mm a dírou projde. Límec Ø40 mm nese jeden bajonetový zub.

Růžička drží satelit v4.6.0. Obrys (0, 0)–(50, 80). T5848 je v (25, 58), LED D4…D11 na kružnici r = 12 mm kolem téhož bodu. RJ45 je v (14, 16) na vnitřní straně. Díry M3: (42, 12), (8, 40), (42, 66), (8, 74).

Šest kabelů Cat6 se stříhá na stejnou délku, viz `export/CUT_LENGTHS.txt`. Stožár HT DN 32 se do slepého hrdla zasouvá 40 mm. Tři otvory Ø12 mm na měniče jsou po 120° kolem stožáru, 48 mm od osy.

Podklad [`stl/spojka-echo.stl`](stl/spojka-echo.stl) zůstává jako reference malé spojky. Tištěný střed je koule, protože se do ní vejdou Core a silová deska a plášť je ve všech směrech stejný.

## Desky

[het68_pcb v4.6.0](https://github.com/fedurca/het68_pcb/releases/tag/v4.6.0):

- Core 160 × 100 mm, šest RJ45 v řadě na y = 10 mm: x = 14, 38, 62, 86, 110, 134. `J_PWR` je v (42, 92). Díry M3: H1 (4,95, 70,95), H2 (6, 94), H3 (154, 6), H4 (154, 94).
- Silová deska 140 × 80 mm, tři SKU se stejným obrysem. Držák Keystone 1122 je v (78, 62), `J_CORE` v (18, 48). Díry M3: (4, 4), (4, 76), (136, 4), (136, 76).
- Satelit 50 × 80 mm, šest kusů. Obrys je obdélník (0, 0)–(50, 80).

Satelit, souřadnice desky v mm:

- akustický port T5848 (`MK1`) je v (25, 58) na vnitřní straně, vrtání 0,8 mm. Na venkovní straně (F.Cu) je jen tento port a osm LED
- LED D4…D11 leží na kružnici o poloměru 12 mm kolem (25, 58), pouzdro 5 × 5 mm
- RJ45 `J1` (Amphenol RJHSE538X) je v (14, 16), otočený o 180°, na vnitřní straně. Tělo má půdorys zhruba x 0,7…20 a y 7,5…24. Hrana y = 0 míří k zemi
- díry M3: H1 (42, 12), H2 (8, 40), H3 (42, 66), H4 (8, 74), vrtání 3,2 mm

RJ45 zástrčka má průřez 11,7 × 8 mm a projde dírou Ø28,4 mm.
