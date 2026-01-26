# LuaLaTeX Font Constructor Example

This example demonstrates how to modify fonts using LuaLaTeX font constructors with Harfbuzz renderer. The technique is based on a discussion from the [babel GitHub repository](https://github.com/latex3/babel/discussions/346).

## Overview

This example shows how to:
- Define a custom font feature using Lua
- Modify character properties (width, color) in a font
- Register the feature with the font constructor system
- Apply the feature using fontspec

## Requirements

- LuaLaTeX (not pdfLaTeX or XeLaTeX)
- fontspec package
- FreeSerif font (or any other TrueType/OpenType font)

## What It Does

The example creates a font feature called "redden" that:
1. Identifies vowels (a, e, i, o, u, ó) in the font
2. Sets their width to 7pt
3. Changes their color to red using PDF special commands

## How It Works

### 1. Define the Manipulator Function

```lua
function redden(f)
  local u = unicode.utf8
  for i, v in pairs(f.characters) do
    if i < 256 and u.find(u.char(i), '[aeiouó]') then
      v.width = tex.sp('7pt')
      v.commands = {
        { "special", "pdf: 1 0 0 rg" },
        { "char", i },
        { "special", "pdf: 0 g" }
      }
    end
  end
end
```

This function:
- Iterates through all characters in the font
- Checks if the character is a vowel
- Modifies the character's width property
- Adds PDF special commands to change color

### 2. Register the Font Feature

```lua
fonts.constructors.features.otf.register {
  name = "redden",
  manipulators = {
    base = redden, % Base renderer
    node = redden, % Node renderer
    plug = redden  % Harfbuzz renderer
  }
}
```

The feature is registered for all three renderers:
- **base**: Base renderer
- **node**: Node renderer  
- **plug**: Harfbuzz renderer (required for modern font shaping)

### 3. Apply the Feature

```latex
\setmainfont[RawFeature=+redden, Renderer=Harfbuzz]{FreeSerif}
```

The font is loaded with:
- `RawFeature=+redden`: Activates our custom feature
- `Renderer=Harfbuzz`: Uses the Harfbuzz renderer

## Virtual Font Commands

The `v.commands` table accepts virtual font (VF) commands. Common commands include:

- `{ "char", <charcode> }`: Insert a character
- `{ "special", <string> }`: Insert a PDF special command
- `{ "push" }`: Save current position
- `{ "pop" }`: Restore saved position
- `{ "right", <distance> }`: Move right
- `{ "down", <distance> }`: Move down

LuaTeX adds additional commands to the basic VF set. See the LuaTeX manual for complete documentation.

## Use Cases

This technique can be used for:
- Creating language-specific typographic features
- Implementing custom ligatures
- Adjusting character spacing or positioning
- Adding visual effects to specific characters
- Creating specialized fonts for specific purposes

## Related Resources

- **luaotfload-szss.lua**: Example of adding ligatures using constructors
- **LuaTeX Manual**: Complete documentation of VF commands and font handling
- **fonts-mkiv.pdf**: Documentation of font features and handlers
- **Fonts & Encodings** by Yannis Haralambous: Comprehensive guide to font technology

## Compiling

To compile this example:

```bash
lualatex font-constructor-example.tex
```

## Note on Babel Integration

When using with babel, you can use `\babelfont` to assign different fonts (with different constructors) to different languages:

```latex
\babelfont[spanish]{rm}[RawFeature=+redden, Renderer=Harfbuzz]{FreeSerif}
```

This is particularly useful when a constructor is designed for a specific language.

## Limitations

- This technique only works with LuaLaTeX
- Since `fonts.handlers.otf.addfeature` doesn't work with Harfbuzz, constructors are the recommended approach
- Fonts cannot be modified once loaded, so the manipulator function runs during font loading
- The example is intentionally simple and unrealistic for demonstration purposes

## Credits

This example is based on a discussion in the babel project. The original content was shared in [babel discussions #346](https://github.com/latex3/babel/discussions/346).
