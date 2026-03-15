"""
Terrain analysis and generation tool handlers.

This module contains handlers for terrain-related operations including
analysis, generation, texturing, and smoothing.
"""

from typing import Dict, Any, List, Optional
from mcp.types import TextContent


async def handle_generate_terrain(
    arguments: Dict[str, Any], rcon: Any, config: Any, logger_instance: Any
) -> List[TextContent]:
    """Handle generate_terrain tool."""
    from ..terrain_generation import TerrainGenerator

    terrain_type = arguments.get("type")
    x1, y1, z1 = arguments.get("x1"), arguments.get("y1"), arguments.get("z1")
    x2, y2, z2 = arguments.get("x2"), arguments.get("y2"), arguments.get("z2")

    # Optional parameters (vary by terrain type)
    scale = arguments.get("scale")
    amplitude = arguments.get("amplitude")
    depth = arguments.get("depth")
    height = arguments.get("height")
    direction = arguments.get("direction")
    octaves = arguments.get("octaves")
    smooth_iterations = arguments.get("smooth_iterations")
    seed = arguments.get("seed")

    try:
        generator = TerrainGenerator(rcon)

        # Call appropriate generation method based on type
        cx1, cy1, cz1 = int(x1 or 0), int(y1 or 0), int(z1 or 0)
        cx2, cy2, cz2 = int(x2 or 0), int(y2 or 0), int(z2 or 0)

        if terrain_type == "rolling_hills":
            hills_kwargs: Dict[str, Any] = {}
            if scale is not None:
                hills_kwargs["scale"] = int(scale)
            if amplitude is not None:
                hills_kwargs["amplitude"] = int(amplitude)
            if octaves is not None:
                hills_kwargs["octaves"] = int(octaves)
            if smooth_iterations is not None:
                hills_kwargs["smooth_iterations"] = int(smooth_iterations)
            if seed is not None:
                hills_kwargs["seed"] = int(seed)
            result = generator.generate_hills(cx1, cy1, cz1, cx2, cy2, cz2, **hills_kwargs)

        elif terrain_type == "rugged_mountains":
            mountains_kwargs: Dict[str, Any] = {}
            if scale is not None:
                mountains_kwargs["scale"] = int(scale)
            if amplitude is not None:
                mountains_kwargs["amplitude"] = int(amplitude)
            if octaves is not None:
                mountains_kwargs["octaves"] = int(octaves)
            if smooth_iterations is not None:
                mountains_kwargs["smooth_iterations"] = int(smooth_iterations)
            if seed is not None:
                mountains_kwargs["seed"] = int(seed)
            result = generator.generate_mountains(cx1, cy1, cz1, cx2, cy2, cz2, **mountains_kwargs)

        elif terrain_type == "valley_network":
            valleys_kwargs: Dict[str, Any] = {}
            if scale is not None:
                valleys_kwargs["scale"] = int(scale)
            if depth is not None:
                valleys_kwargs["depth"] = int(depth)
            if octaves is not None:
                valleys_kwargs["octaves"] = int(octaves)
            if smooth_iterations is not None:
                valleys_kwargs["smooth_iterations"] = int(smooth_iterations)
            if seed is not None:
                valleys_kwargs["seed"] = int(seed)
            result = generator.generate_valleys(cx1, cy1, cz1, cx2, cy2, cz2, **valleys_kwargs)

        elif terrain_type == "mountain_range":
            range_kwargs: Dict[str, Any] = {}
            if direction is not None:
                range_kwargs["direction"] = str(direction)
            if scale is not None:
                range_kwargs["scale"] = int(scale)
            if amplitude is not None:
                range_kwargs["amplitude"] = int(amplitude)
            if octaves is not None:
                range_kwargs["octaves"] = int(octaves)
            if smooth_iterations is not None:
                range_kwargs["smooth_iterations"] = int(smooth_iterations)
            if seed is not None:
                range_kwargs["seed"] = int(seed)
            result = generator.generate_mountain_range(cx1, cy1, cz1, cx2, cy2, cz2, **range_kwargs)

        elif terrain_type == "plateau":
            plateau_kwargs: Dict[str, Any] = {}
            if height is not None:
                plateau_kwargs["height"] = int(height)
            if smooth_iterations is not None:
                plateau_kwargs["smooth_iterations"] = int(smooth_iterations)
            if seed is not None:
                plateau_kwargs["seed"] = int(seed)
            result = generator.generate_plateau(cx1, cy1, cz1, cx2, cy2, cz2, **plateau_kwargs)

        else:
            return [TextContent(type="text", text=f"❌ Unknown terrain type: {terrain_type}")]

        if not result.get("success"):
            return [
                TextContent(type="text", text=f"❌ Error: {result.get('error', 'Unknown error')}")
            ]

        # Format output
        output = "🏔️ Terrain Generation Complete\n\n"
        output += f"**Type:** {result['terrain_type'].replace('_', ' ').title()}\n"
        output += f"**Summary:** {result['summary']}\n\n"

        output += "**Parameters Used:**\n"
        for key, value in result.get("parameters", {}).items():
            output += f"  - {key}: {value}\n"
        output += "\n"

        output += "**Operations Performed:**\n"
        for i, (operation, step_result) in enumerate(result.get("steps", []), 1):
            output += f"  {i}. {operation}\n"
            if operation == "Selection" and step_result.get("success"):
                region = step_result.get("region", {})
                output += f"     Region: {region.get('volume', 0):,} blocks\n"
        output += "\n"

        output += "**Next Steps:**\n"
        output += "  • Apply texturing with texture_terrain() for natural appearance\n"
        output += "  • Add additional smoothing if needed with smooth_terrain()\n"
        output += "  • Overlay vegetation, water features, or structures\n"

        logger_instance.info(
            f"Terrain generation complete: {terrain_type} at ({x1},{y1},{z1}) to ({x2},{y2},{z2})"
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error generating terrain: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain generation failed: {str(e)}")]


async def handle_texture_terrain(
    arguments: Dict[str, Any], rcon: Any, config: Any, logger_instance: Any
) -> List[TextContent]:
    """Handle texture_terrain tool."""
    from ..terrain_generation import TerrainGenerator

    style = arguments.get("style")
    x1, y1, z1 = arguments.get("x1"), arguments.get("y1"), arguments.get("z1")
    x2, y2, z2 = arguments.get("x2"), arguments.get("y2"), arguments.get("z2")

    try:
        generator = TerrainGenerator(rcon)
        result = generator.texture_natural_slopes(
            int(x1 or 0), int(y1 or 0), int(z1 or 0),
            int(x2 or 0), int(y2 or 0), int(z2 or 0),
            str(style) if style is not None else "temperate",
        )

        if not result.get("success"):
            return [
                TextContent(type="text", text=f"❌ Error: {result.get('error', 'Unknown error')}")
            ]

        # Format output
        output = "🎨 Terrain Texturing Complete\n\n"
        output += f"**Style:** {style.title() if style is not None else 'temperate'}\n"
        output += f"**Summary:** {result['summary']}\n\n"

        recipe = result.get("recipe", {})
        output += "**Materials Applied:**\n"
        output += f"  - Base: {recipe.get('base', 'N/A')}\n"
        output += f"  - Surface: {recipe.get('surface', 'N/A')}\n\n"

        output += "**Operations Performed:**\n"
        for i, (operation, step_result) in enumerate(result.get("steps", []), 1):
            output += f"  {i}. {operation}\n"
        output += "\n"

        output += "**Texture applied successfully!** Your terrain now has a natural appearance.\n"

        logger_instance.info(
            f"Terrain texturing complete: {style} style at ({x1},{y1},{z1}) to ({x2},{y2},{z2})"
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error texturing terrain: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain texturing failed: {str(e)}")]


async def handle_smooth_terrain(
    arguments: Dict[str, Any], rcon: Any, config: Any, logger_instance: Any
) -> List[TextContent]:
    """Handle smooth_terrain tool."""
    from ..terrain_generation import TerrainGenerator

    x1, y1, z1 = arguments.get("x1"), arguments.get("y1"), arguments.get("z1")
    x2, y2, z2 = arguments.get("x2"), arguments.get("y2"), arguments.get("z2")
    iterations = arguments.get("iterations", 2)
    mask = arguments.get("mask")

    try:
        generator = TerrainGenerator(rcon)

        # Set selection first
        select_result = generator.set_selection(int(x1 or 0), int(y1 or 0), int(z1 or 0), int(x2 or 0), int(y2 or 0), int(z2 or 0))
        if not select_result.get("success"):
            return [
                TextContent(
                    type="text", text=f"❌ Error: {select_result.get('error', 'Selection failed')}"
                )
            ]

        # Apply smoothing
        result = generator.smooth(iterations, mask)

        if not result.get("success"):
            return [
                TextContent(type="text", text=f"❌ Error: {result.get('error', 'Unknown error')}")
            ]

        # Format output
        output = "✨ Terrain Smoothing Complete\n\n"
        output += f"**Iterations:** {result['iterations']}\n"
        output += f"**Region:** {select_result['region']['volume']:,} blocks\n"
        if mask:
            output += f"**Mask:** {mask}\n"
        output += "\n"

        output += f"**Result:** {result['output']}\n\n"
        output += "Terrain has been smoothed for a more natural appearance.\n"

        logger_instance.info(
            f"Terrain smoothing complete: {iterations} iterations at ({x1},{y1},{z1}) to ({x2},{y2},{z2})"
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error smoothing terrain: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain smoothing failed: {str(e)}")]
