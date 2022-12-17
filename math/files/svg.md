# SVG Structure notes

*Some notes collected from [this website](http://using-d3js.com/05_01_paths.html) and [this website](https://developer.mozilla.org/en-US/docs/Web/SVG), others from the product of [this one](http://www.tlhiv.org/ltxpreview/). Compiled by Miles Robertson, 12/14/22*

## SVG Document Syntax

```xml
<?xml version="1.0" encoding="UTF-8"?>

<svg 
    xmlns="http://www.w3.org/2000/svg"
    width="_pt" 
    height="_pt" 
    viewBox="0 0 _ _" 
    version="1.1">
    <defs>
        <g>
            <symbol overflow="" id="">
                <path style="" d=""/>
            </symbol>
            <symbol><path/></symbol>
            ...
            <symbol><path/></symbol>
        </g>
    </defs>
    <g id="surface_">
        <g style="">
            <use xlink:href="" x="" y=""/>
        </g>
        <g><use/></g>
        ...
        <g><use/></g>
        <path/>
    </g>



</svg>
```

## Paths

The general structure of a symbol object is as follows:

```xml
<symbol overflow="visible" id="">
    <path style="stroke:none;" d=""/>
</symbol>
```
Give `id` a unique string. `d` is a series of `(x, y)` (sometimes more) points that can be defined as follows:

| char | meaning | inputs |
|---|---|---|
| `M` | Move to <br/> (pen up)  | `(x,y)` |
| `L` | Line to <br/> (pen down) | `(x,y)` |
| `Z` | Close path | None |
| `Q` | Quadratic curve to <br/> (quadratic bezier) | `(cpx, cpy, x, y)` |
| `C` | Bezier curve to <br/> (cubic bezier) | `(cpx1, cpy1, cpx2, cpy2, x, y)` |
| `A` | Arc | `(x1, y1, x2, y2, radius)` <br/> or maybe <br/> `(x, y, radius, startAngle, endAngle[, anticlockwise])` |

An example of this is the $\int$ symbol:

```xml
<symbol overflow="visible" id="int1">
    <path 
        style = "stroke:none;" 
        d = "M 2.71875  8.765625 
             C 2.578125 10.40625  2.21875  10.859375 1.65625  10.859375 
             C 1.53125  10.859375 1.21875  10.828125 1.015625 10.640625 
             C 1.3125   10.609375 1.390625 10.375    1.390625 10.234375 
             C 1.390625 9.953125  1.171875 9.8125    0.984375 9.8125 
             C 0.78125  9.8125    0.5625   9.953125  0.5625   10.25 
             C 0.5625   10.71875  1.0625   11.078125 1.65625  11.078125 
             C 2.609375 11.078125 3.078125 10.203125 3.296875 9.3125 
             C 3.421875 8.796875  3.78125  5.890625  3.875    4.78125 
             L 4.0625   2.296875 
             C 4.203125 0.46875   4.53125  0.21875   4.984375 0.21875 
             C 5.078125 0.21875   5.390625 0.234375  5.609375 0.421875 
             C 5.328125 0.46875   5.25     0.703125  5.25     0.84375 
             C 5.25     1.125     5.46875  1.25      5.65625  1.25 
             C 5.859375 1.25      6.078125 1.125     6.078125 0.828125 
             C 6.078125 0.34375   5.578125 0         4.96875  0 
             C 4.03125  0         3.640625 0.96875   3.46875  1.71875 
             C 3.34375  2.265625  2.984375 5.078125  2.90625  6.296875 
             Z 
             M 2.71875 8.765625 "/>
</symbol>
```
Then, this `symbol` is `use`d in a later `g` tag to place it:

```xml
<g style="fill:rgb(0%,0%,0%);fill-opacity:1;">
  <use href="#int1" x="1" y="1" fill="blue" stroke="red"/>
</g>
```
*Note: `xlink:href` is depreciated and should be replaced with `href`*

[The attributes](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/use) of `use`:
- `href`
- `x`, `y` 
- (`width`, `height` are rarely used)
- `clip-path`
- `clip-rule`
- `color`
- `color-interpolation`
- `cursor`
- `display`
- `fill`
- `fill-opacity`
- `fill-rule`
- `filter`
- `mask`
- `opacity`
- `pointer-events`
- `shape-rendering`
- `stroke`
- `stroke-dasharray`
- `stroke-dashoffset`
- `stroke-linecap`
- `stroke-linejoin`
- `stroke-miterlimit`
- `stroke-opacity`
- `stroke-width`
- `transform`
    - This can take several arguments, which can be written one after another, such as follows:
    - `matrix(<a> <b> <c> <d> <e> <f>)`, where each coordinate pair `$x // y // 1$` is multiplied to the matrix `$a | b | c // d | e | f // 0 | 0 | 1$` to obtain the new coordinates.
    - `translate(<x> [<y>])`
    - `scale(<x> [<y>])`
    - `rotate(<x> [<y>])`
    - `skewX(<a>)`, `skewY(<a>)`
- `vector-effect`
- `visibility`


Paths can be rendered outside of A horizontal line might be drawn like this:

```xml
<path 
    style = "fill:none;
             stroke-width:4.05;
             stroke-linecap:butt;
             stroke-linejoin:miter;
             stroke:rgb(0%,0%,0%);
             stroke-opacity:1;
             stroke-miterlimit:10;" 
    d = "M 488.476562 437.304688 
         L 537.617188 437.304688 " 
    transform = "matrix(0.1, 
                        0, 
                        0, 
                        -0.1, 
                        0, 
                        50)"
/>
```

## Alternative Shapes

Some other shapes that can be made:
- `<ellipse>`
- `<image>`
- `<line>`
- `<polygon>`
- `<polyline>`
- `<rect>`
- `<marker>`





