import arcpy




def create_single_map(
    map_name,
    layer_path,
    layer_name,
    renderer,
    variable_name,
    color_map,
    label_map=None,
    classification_method="NaturalBreaks",
    break_count=5
):
    """
    Creates a map and applies symbology to a spatial layer.

    Parameters
    ----------
    map_name : str
        Name assigned to the newly created map.
    layer_path : str
        File path to the spatial dataset added to the map.
    layer_name : str
        Display name for the layer.
    renderer : str
        ArcGIS renderer type ('UniqueValueRenderer' or 'GraduatedColorsRenderer').
    variable_name : str
        Attribute field used for symbology.
    color_map : str
        Name of the ArcGIS color ramp.
    label_map : dict, optional
        Mapping of attribute values to display labels.
    classification_method : str, optional
        Classification method for graduated symbology.
    break_count : int, optional
        Number of classes for graduated symbology.

    Returns
    -------
    map_obj : arcpy.mp.Map
        The created map object.
    layer : arcpy.mp.Layer
        The styled layer added to the map.
    """

    m = aprx.createMap(map_name)
    layer = m.addDataFromPath(layer_path)
    layer.name = layer_name

    # Remove default basemap layers
    for lyr in m.listLayers():
        if lyr.isBasemapLayer:
            m.removeLayer(lyr)

    sym = layer.symbology
    sym.updateRenderer(renderer)

    ramp = aprx.listColorRamps(color_map)[0]
    sym.renderer.colorRamp = ramp

    # Unique value symbology
    if renderer == "UniqueValueRenderer":
        sym.renderer.fields = [variable_name]

        items = sym.renderer.groups[0].items
        items.sort(key=lambda g: g.values[0][0])

        for item in items:
            val = int(item.values[0][0])
            item.label = label_map.get(val, str(val))

    # Graduated color symbology
    elif renderer == "GraduatedColorsRenderer":
        sym.renderer.classificationField = variable_name
        sym.renderer.classificationMethod = classification_method
        sym.renderer.breakCount = break_count
        sym.renderer.reclassify()

    else:
        raise ValueError(f"Unsupported renderer: {renderer}")

    layer.symbology = sym
    return m, layer




def create_standard_layout(
    map_obj,
    layer,
    layout_name,
    title_text,
    mapframe_extent=None,
    title_position=(4.1215, 5.539),
    legend_position=(0.1464, 2.2927),
    legend_size=(1.2357, 1.7131),
    scalebar_position=(2.7713, 0.2371),
    north_arrow_position=(7.2704, 4.8844)
):
    """
    Creates a standardized map layout with title, legend, scale bar,
    and north arrow.

    Parameters
    ----------
    map_obj : arcpy.mp.Map
        Map object to be placed in the layout.
    layer : arcpy.mp.Layer
        Layer used to set the map extent.
    layout_name : str
        Name assigned to the layout.
    title_text : str
        Title displayed on the layout.
    mapframe_extent : arcpy.Extent, optional
        Page coordinates for the map frame.
    title_position : tuple, optional
        Position of the title text element.
    legend_position : tuple, optional
        Position of the legend.
    legend_size : tuple, optional
        Width and height of the legend.
    scalebar_position : tuple, optional
        Position of the scale bar.
    north_arrow_position : tuple, optional
        Position of the north arrow.

    Returns
    -------
    layout : arcpy.mp.Layout
        The generated layout object.
    """

    layout = aprx.createLayout(8.27, 5.83, "INCH", layout_name)

    if mapframe_extent is None:
        mapframe_extent = arcpy.Extent(0.885, 0.665, 7.385, 5.165)

    mf = layout.createMapFrame(mapframe_extent, map_obj)

    # Remove map frame border
    lyt_cim = layout.getDefinition("V3")
    for elm in lyt_cim.elements:
        if type(elm).__name__ == "CIMMapFrame":
            elm.graphicFrame.borderSymbol = None
    layout.setDefinition(lyt_cim)

    # Zoom map frame to layer extent
    mf.camera.setExtent(mf.getLayerExtent(layer))

    # Title element
    txt_style = aprx.listStyleItems("ArcGIS 2D", "TEXT", "Title (Serif)")[0]
    title = aprx.createTextElement(
        layout,
        arcpy.Point(*title_position),
        "POINT",
        title_text,
        20,
        style_item=txt_style
    )

    title.setAnchor("Center_Point")
    title.fontFamilyName = "Garamond"

    # Legend
    legend_style = aprx.listStyleItems("ArcGIS 2D", "LEGEND", "Legend 1")[0]
    legend = layout.createMapSurroundElement(
        arcpy.Point(*legend_position),
        "LEGEND",
        mf,
        legend_style
    )

    legend.elementWidth = legend_size[0]
    legend.elementHeight = legend_size[1]

    leg_cim = legend.getDefinition("V3")
    for item in leg_cim.items:
        item.showLayerName = False
        item.showHeading = False
    legend.setDefinition(leg_cim)

    # Scale bar
    scalebar_style = aprx.listStyleItems(
        "ArcGIS 2D",
        "SCALE_BAR",
        "Scale Line 1 Metric"
    )[0]

    layout.createMapSurroundElement(
        arcpy.Point(*scalebar_position),
        "SCALE_BAR",
        mf,
        scalebar_style
    )

    # North arrow
    north_arrow_style = aprx.listStyleItems(
        "ArcGIS 2D",
        "NORTH_ARROW",
        "ArcGIS North 1"
    )[0]

    layout.createMapSurroundElement(
        arcpy.Point(*north_arrow_position),
        "NORTH_ARROW",
        mf,
        north_arrow_style
    )

    return layout
