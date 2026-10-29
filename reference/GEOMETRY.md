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

Starý kříž na fotce má jedno rameno svisle a stožár v dolním portu. To s `MIC_DIR` nesedí. Desky jsou ve středu sedmispojky, protože kabely od satelitů mají společný limit délky. Plášť je válec, takže všech šest ramen vidí stejnou překážku ve stejné vzdálenosti. Samostatná skříň pod dolním vrcholem by horní a dolní kabely rozhodila.

## Desky

[het68_pcb v4.5.0](https://github.com/fedurca/het68_pcb/releases/tag/v4.5.0):

- Core 160 × 100 mm, silová deska 140 × 80 mm, držák článku 21700. Stoh se do skříně vejde jako obálka 160 × 100 × 54 mm.
- Satelit 50 × 80 mm, šest kusů. Obrys v KiCadu je obdélník (0,0)–(50,80).

Satelit, souřadnice desky v mm:

- akustický port T5848 (`MK1`) je v (25, 58,708), vrtání 0,8 mm. Na venkovní straně desky (F.Cu) je jen tento port a osm LED
- LED D4…D11 leží na kružnici o poloměru 12 mm kolem (25, 58), pouzdro 5 × 5 mm
- RJ45 `J1` (Amphenol RJHSE538X) je u hrany y=0, půdorys zhruba x 0,7…20 a y 7,5…24. Ta hrana míří k zemi
- díry M3: H1 (42, 12), H2 (8, 40), H3 (42, 66), H4 (8, 74), vrtání 3,2 mm

RJ45 zástrčka má asi 12 × 8 mm a projde dírou Ø28,4 mm.
