# Stereoplot Interactive Structural Data Visualisation Plugin ![Stereoplot icon](icon.png)  
*author: [Julien Perret](mailto:julien.perret@uwa.edu.au) & [Mark Jessell](mailto:mark.jessell@uwa.edu.au)*  
*version 1.0.0 - June 2026*

# Changelog 1.0.0

**Major Functional Improvements**

- Added automatic structural data-type detection for **Planes Only**, **Lineations Only**, and **Lineations with Bearing Planes** datasets.
- Added lower-hemisphere, equal-area stereonet plotting for planar and linear structural measurements.
- Added rose-diagram plotting for orientation-frequency visualisation.
- Added density contouring using Modified Kamb sigma-level contours.
- Added best-fit girdle calculation and dynamic fabric-statistic reporting.
- Added lineation-bearing plane visualisation for combined planar-linear datasets.
- Added kinematic arrow plotting for recognised shear-sense or slip-sense attributes.
- Added attribute-based classification, category visibility controls, and category-specific style editing.
- Added data filtering using native QGIS expressions.
- Added interactive stereonet selection linked to selected QGIS features.
- Added figure export with stereonet elements, legends, colour bars, contours, girdles, and rose diagrams.
- Added project-level persistence of plotting settings and style templates.

> [!TIP]
> Stereoplot was designed as a lightweight QGIS companion for structural geologists who need to move rapidly from mapped or imported structural measurements to stereonet-based visual inspection, filtering, classification, and publication-ready figure export.

---

## 1. Description

**Stereoplot** is an open-source QGIS plugin for the interactive stereographic projection, visualisation, filtering, classification, and first-pass analysis of structural geology datasets.

The plugin plots structural measurements from selected QGIS vector layers on **lower-hemisphere, equal-area stereonets** and **rose diagrams**. It supports planar fabrics, linear fabrics, and combined lineation-bearing plane datasets, including structural measurements collected in GEOL-QMAPS-compatible layers or stored in more general point shapefile or GeoPackage architectures.

![PluginButtons](PluginButtons.PNG)

Stereoplot is intended for:

- rapid inspection of field structural measurements;
- visual comparison of planar and linear fabric populations;
- structural-domain analysis using attribute classification and filtering;
- kinematic visualisation of lineation-bearing plane datasets;
- preliminary fabric analysis using density contours and best-fit girdles;
- export of clean stereonet and rose-diagram figures for reports, teaching material, and publications.

> [!IMPORTANT]
> Stereoplot is a plotting and exploratory analysis tool. Geological interpretation remains the responsibility of the user and must be based on field context, measurement quality, structural overprinting relationships, and the geological question being addressed.

---

## 2. Citation

No dedicated publication describing Stereoplot is available at this stage.

If you use Stereoplot in a publication, report, teaching resource, or internal workflow, please cite or acknowledge the repository and the main contributors:

> *Perret, J. & Jessell, M.W., 2026. Stereoplot: an interactive QGIS plugin for stereographic projection and structural data visualisation. GitHub repository: [https://github.com/swaxi/Stereoplot](https://github.com/swaxi/Stereoplot).* 

Stereoplot builds on the stereographic projection functionality of **mplstereonet** and was redeveloped from concepts used in earlier QGIS stereonet tools. Please also acknowledge these projects where appropriate.

---

## 3. Software Specifications

Stereoplot is a QGIS plugin written in Python and using Matplotlib-based plotting.

| Component | Requirement / status |
|---|---|
| GIS platform | QGIS Desktop |
| Minimum QGIS version | 3.0.0 |
| Maximum QGIS version | 4.99 |
| Qt6 support | Yes |
| Processing provider | No |
| Main plotting backend | Matplotlib + mplstereonet |
| Supported geometry | Vector layers, primarily point layers containing structural attributes |
| Licence | MIT licence, as provided in the repository |

> [!IMPORTANT]
> Make sure that the plugin version is compatible with your QGIS installation. If QGIS reports that the plugin is broken, first check that the plugin folder name, `metadata.txt`, bundled dependencies, and QGIS version are consistent.

---

## 4. Installation

### *4.1. Installation from ZIP*

1. Download the latest ZIP package from the [Stereoplot GitHub repository](https://github.com/swaxi/Stereoplot).
2. Open **QGIS Desktop**.
3. Go to **Plugins > Manage and Install Plugins...**.
4. Select **Install from ZIP**.
5. Browse to the downloaded Stereoplot ZIP file.
6. Click **Install Plugin**.
7. Activate the plugin if it is not enabled automatically.

### *4.2. Installation from a cloned repository*

For development or testing:

```bash
git clone https://github.com/swaxi/Stereoplot.git
```

Then copy or symlink the `Stereoplot` folder into your QGIS plugin directory.

Typical Windows plugin directory:

```text
C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

Typical Linux plugin directory:

```text
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

Typical macOS plugin directory:

```text
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```

Restart QGIS and enable Stereoplot from the Plugin Manager.

> [!CAUTION]
> The plugin folder name should remain consistent with the plugin metadata. Avoid nested folders such as `Stereoplot-main/Stereoplot`, which may prevent QGIS from loading the plugin correctly.

---

## 5. Workflow

The general Stereoplot workflow is intentionally simple:

1. load a structural dataset into QGIS;
2. select the layer and the structural features to plot;
3. configure plotting options;
4. generate the stereonet or rose diagram;
5. classify, filter, style, interpret, and export the result.

![SettingsWindow](SettingsWindow.PNG)

### *5.1. Quick Start Guide*

#### 5.1.1. Select a structural layer

Select a point layer containing structural measurements in the QGIS **Layers** panel.

The plugin inspects the selected layer and attempts to detect whether it contains:

- planar measurements;
- linear measurements;
- lineations with associated bearing planes.

#### 5.1.2. Select the features to plot

Use standard QGIS selection tools to select the features to be plotted.

> [!CAUTION]
> The QGIS **Identify Features** tool does not create a feature selection. Use a true selection tool, such as **Select Features by Area or Single Click**, **Select by Expression**, or **Select by Location**.

#### 5.1.3. Open the Stereoplot settings

Click the **Stereonet Settings** button to configure the plot.

Available settings include:

- data type to plot;
- great circles;
- contours;
- lineation-bearing planes;
- rose diagram mode;
- kinematics;
- best-fit girdle;
- classification;
- filtering.

#### 5.1.4. Generate the plot

Click the **Stereonet** button.

Stereoplot reads the selected features, extracts recognised structural fields, applies any active filter or classification, and opens the plot window.

---

## 6. Detailed Functionality

### *6.1. Automatic Structural Data-Type Detection*

Stereoplot automatically checks selected vector layers for recognised structural fields.

| Detected data type | Required measurements | Typical display |
|---|---|---|
| **Planes Only** | Strike + Dip, or Dip Direction + Dip | poles to planes, great circles, contours, rose diagrams |
| **Lineations Only** | Trend/Azimuth/Bearing + Plunge | lineations, contours, rose diagrams |
| **Lineations with Bearing Planes** | Trend/Azimuth/Bearing + Plunge, plus Strike/Dip or Dip Direction/Dip for the associated plane | lineations, bearing planes, kinematic arrows, contours |

> [!TIP]
> Automatic detection is useful for routine work, but the **Data to plot** dropdown can be used to override the detected mode when a dataset contains ambiguous or non-standard field combinations.

### *6.2. Stereonet Plotting*

Stereoplot uses a lower-hemisphere, equal-area projection for stereonet plots.

Supported stereonet elements include:

- poles to planes;
- great circles;
- lineations;
- lineation-bearing planes;
- kinematic arrows;
- density contours;
- best-fit girdles;
- classification legends.

![GreatCircles](GreatCircles.PNG)

#### Planar datasets

Planar datasets may be plotted as:

- **poles to planes**, useful for fold-axis estimation, cleavage/foliation clustering, and structural-domain comparison;
- **great circles**, useful for direct visualisation of bedding, foliation, shear planes, veins, faults, or axial planes.

#### Linear datasets

Linear datasets may be plotted as points representing trend and plunge. This is appropriate for mineral lineations, stretching lineations, fold axes, intersection lineations, slickensides, or palaeocurrent indicators, provided that the measurements are consistently encoded.

#### Combined planar-linear datasets

Combined datasets can display lineations together with their associated bearing planes. This is particularly useful for shear-sense indicators, slickenlines on fault planes, stretching lineations within shear fabrics, and fold axes associated with axial surfaces.

---

## 7. Data Requirements

### *7.1. Layer and Geometry Requirements*

Stereoplot is designed primarily for QGIS vector layers containing structural measurements as attributes. Point layers are the standard use case, although the plugin reads attributes rather than relying on point geometry for stereonet calculations.

Recommended formats include:

- GeoPackage (`.gpkg`);
- ESRI Shapefile (`.shp`);
- temporary QGIS scratch layers;
- GEOL-QMAPS-compatible structural layers.

> [!TIP]
> Store structural measurements in numeric fields wherever possible. Text fields containing values such as `045`, `45°`, or `45 deg` may require cleaning before plotting.

### *7.2. Recognised Structural Fields*

Stereoplot recognises several common field-name variants.

| Measurement | Recognised field names |
|---|---|
| Strike | `Strike_RHR`, `Strike`, `strike` |
| Dip direction | `Dip_Direction`, `Dip_Dir`, `DipDirection`, `dip_direction`, `DipDir`, `DIPDIR` |
| Dip | `Dip`, `dip` |
| Trend / azimuth / bearing | `Azimuth`, `azimuth`, `Bearing`, `bearing`, `Trend`, `TREND` |
| Plunge | `Plunge`, `plunge` |
| Associated bearing-plane strike | `Strike_ref`, `Strike_Ref`, `strike_ref` |
| Associated bearing-plane dip direction | `DipDir_ref`, `Dip_Dir_ref`, `DipDirection_ref`, `Dip_Direction_ref`, `DipDirection_Ref`, `dipdir_ref`, `dip_dir_ref`, `dip_direction_ref` |
| Associated bearing-plane dip | `Dip_ref`, `Dip_Ref`, `dip_ref` |
| Kinematics | `Kinematics`, `kinematics`, `Kinematic`, `kinematic`, `Kin`, `kin`, `Movement`, `movement`, `SlipSense`, `Slip_Sense`, `slip_sense`, `ShearSense`, `Shear_Sense`, `shear_sense`, `SenseOfMovement`, `Sense_of_Movement`, `sense_of_movement` |
| Pitch | `Pitch_RHR`, `Pitch_rhr`, `Pitch_Rhr`, `Pitch`, `pitch_rhr`, `RHR_pitch`, `rhr_pitch`, `pitch` |

### *7.3. Measurement Conventions*

For planar data, Stereoplot can use either:

- **Strike + Dip**, with strike assumed to follow the right-hand rule where relevant;
- **Dip Direction + Dip**.

For linear data, Stereoplot uses:

- **Trend / Azimuth / Bearing**;
- **Plunge**.

For combined lineation-bearing plane datasets, the lineation and the associated plane must be recorded on the same feature.

> [!CAUTION]
> Do not mix strike conventions within the same field. If part of the dataset uses right-hand-rule strike and another part uses arbitrary strike, great circles, poles, and kinematic arrows may be incorrectly plotted.

---

## 8. Plot Types and Visualisation Options

### *8.1. Stereonet*

The stereonet view is the main Stereoplot output. It supports structural points, great circles, contours, girdles, kinematic arrows, and classification legends.

Recommended use cases:

| Geological question | Useful options |
|---|---|
| Are foliations clustered or dispersed? | Poles to planes + contours |
| Is a fold axis defined by bedding poles? | Poles to planes + best-fit girdle |
| Do lineations define multiple populations? | Lineations + classification + filtering |
| Are shear-sense indicators consistent? | Lineations with bearing planes + kinematic arrows |
| Are structural generations distinct? | Classification by generation, domain, lithology, or kinematics |

### *8.2. Great Circles*

Great-circle plotting is available for planar or combined datasets.

![GreatCircles](GreatCircles.PNG)

Use great circles when direct plane orientation is more informative than poles alone, for example when comparing shear zones, bedding, veins, or fault planes.

### *8.3. Rose Diagrams*

Rose diagrams provide azimuthal frequency plots for structural orientations.

![RoseDiagrams](RoseDiagrams.PNG)

Rose diagrams may be useful for:

- strike-frequency analysis of planar datasets;
- trend-frequency analysis of lineations;
- quick comparison of structural grain between domains;
- identifying dominant orientation families prior to stereonet interpretation.

> [!IMPORTANT]
> Rose diagrams flatten three-dimensional orientation information into azimuthal frequency distributions. They should not be used as a substitute for stereonet analysis where plunge, dip, and full 3D geometry matter.

---

## 9. Classification and Filtering Tools

### *9.1. Attribute-Based Classification*

Classification allows selected features to be grouped by any attribute field in the selected layer.

Useful classification fields include:

- structural generation;
- lithology;
- domain;
- deformation zone;
- kinematic class;
- structure type;
- confidence level;
- observer;
- campaign or field mission.

![Classification-InteractiveLegend-Styling](Classification-InteractiveLegend-Styling.PNG)

When classification is enabled, Stereoplot automatically generates categories from unique attribute values and displays an interactive category legend.

### *9.2. Category Visibility*

For each category, users can:

- show or hide individual categories;
- select all categories;
- hide all categories;
- invert category visibility.

The plot updates dynamically without needing to recreate the stereonet.

### *9.3. Category Styling*

Each category may be styled independently.

Supported styling options include:

- symbol shape;
- symbol colour;
- symbol size;
- line colour;
- line width;
- transparency;
- arrow colour.

### *9.4. Style Templates*

Style templates can be:

- saved;
- loaded;
- reset;
- deleted.

Project-level style persistence is stored in:

```text
stereonet_styles.json
```

Stereoplot settings are stored in:

```text
stereonet.json
```

where project-level configuration is available, with QSettings used as a fallback.

### *9.5. Attribute Filtering*

Stereoplot uses native QGIS expressions for filtering.

Examples:

```sql
"Generation" = 'D2'
```

```sql
"Kinematics" IN ('Sinistral-slip', 'Reverse-slip')
```

```sql
"Generation" = 'D2'
AND "Kinematics" IS NOT NULL
```

Filtering can be used before plotting or during exploratory analysis to reduce a dataset to the population relevant to the geological question.

> [!TIP]
> Use QGIS field aliases for readable forms, but keep provider field names short, stable, and explicit. Stereoplot stores and evaluates the real field name, not only the displayed alias.

---

## 10. Kinematic Analysis Tools

### *10.1. Purpose*

Kinematic arrows are designed to visualise inferred hangingwall displacement directions for lineation-bearing plane datasets.

![LineationsFilteringKinematics](LineationsFilteringKinematics.PNG)

The tool is particularly useful for:

- fault-slip datasets;
- shear-zone datasets;
- lineations with associated shear-sense indicators;
- combined planar-linear measurements collected in the field.

### *10.2. Required Data*

Kinematic arrows require, for each plotted feature:

- a valid lineation orientation;
- a valid associated bearing-plane orientation;
- a recognised kinematic value.

Features lacking one of these components may still be plotted as lineations, but they will not generate kinematic arrows.

### *10.3. Recognised Kinematic Classes*

| Interpreted class | Recognised examples |
|---|---|
| Sinistral | `Sinistral`, `Sinistral-slip`, `Left-lateral`, `Sin` |
| Dextral | `Dextral`, `Dextral-slip`, `Right-lateral`, `Dex` |
| Normal | `Normal`, `Normal-slip`, `Extensional` |
| Reverse | `Reverse`, `Reverse-slip`, `Thrust`, `Compressional` |

Values such as `Unknown`, `Undefined`, `Undetermined`, `N/A`, or equivalent non-diagnostic entries should be treated as non-plottable for kinematic arrows.

### *10.4. Arrow Anchor Position*

The settings dialog allows users to choose the position of the hangingwall displacement arrow:

- **Plane pole**;
- **Lineation**.

> [!CAUTION]
> Kinematic arrows are visual aids. They do not validate the geological interpretation of movement sense. Always check whether the lineation, bearing plane, facing direction, and shear-sense convention are geologically meaningful for the structure being plotted.

---

## 11. Contouring and Statistical Analysis

### *11.1. Density Contours*

Stereoplot supports density contouring for:

- poles to planes;
- lineations;
- lineations with bearing planes.

Density contouring uses Modified Kamb-style sigma-level visualisation through the stereonet plotting backend.

Contour outputs include:

- continuous colour scaling;
- sigma-level contour labels;
- colour-bar display;
- dynamic recalculation when visible categories or filters change.

> [!TIP]
> Use contours on sufficiently populated datasets. For small datasets, individual points may be more informative than smoothed density fields.

### *11.2. Best-Fit Girdle*

Best-fit girdle analysis can be calculated from the currently visible dataset.

![BestFitGirdle](BestFitGirdle.PNG)

The girdle updates dynamically when:

- categories are hidden or shown;
- filters are modified;
- classification settings change.

This is useful for estimating fold-axis trends from girdle distributions, checking whether foliations form a coherent great-circle distribution, or comparing structural domains.

### *11.3. Fabric Statistics*

Stereoplot reports basic fabric statistics based on covariance eigenvalues.

#### Woodcock K-value

```text
K = ln(e1/e2) / ln(e2/e3)
```

where:

```text
e1 ≥ e2 ≥ e3
```

are covariance eigenvalues.

#### Fabric strength C

```text
C = ln(e1/e3)
```

Higher values indicate stronger preferred orientation in the plotted population.

> [!IMPORTANT]
> Statistical outputs should be interpreted as descriptive fabric indicators, not as standalone geological proof. Data clustering, structural-domain mixing, sampling bias, and repeated measurements from the same outcrop can strongly affect the result.

---

## 12. Export Options

Stereoplot figures can be exported directly from the plot window.

Exported figures may include:

- stereonet frame;
- poles, lineations, or great circles;
- bearing planes;
- density contours;
- colour scales;
- best-fit girdles;
- classification legends;
- rose diagrams;
- kinematic arrows.

Recommended export workflow:

1. apply filters and category visibility settings;
2. refine category styling;
3. check legend readability;
4. resize the plot window if needed;
5. export the final figure.

> [!TIP]
> For publication figures, export separate versions for exploratory analysis and final interpretation. Keep the exploratory version with all data visible and the final version with only the interpreted structural population highlighted.

---

## 13. Tips and Warnings

### *13.1. Best-Practice Recommendations*

> [!TIP]
> **Prepare structural fields before plotting.** Use clear numeric fields for strike, dip direction, dip, trend, and plunge. Avoid mixing text, symbols, and numbers in the same measurement field.

> [!TIP]
> **Separate structural populations logically.** Use attributes such as `Generation`, `Domain`, `Lithology`, `Structure_Type`, or `Confidence` so that classification and filtering can be used effectively.

> [!TIP]
> **Use projected CRS for map-based structural workflows.** Although stereonet calculations use orientation attributes rather than map geometry, structural data preparation and validation in QGIS are usually clearer in an appropriate projected CRS.

> [!TIP]
> **Check measurement conventions before interpretation.** Confirm whether planar data are stored as right-hand-rule strike/dip or dip-direction/dip before plotting great circles, poles, or kinematic arrows.

> [!TIP]
> **Filter before contouring.** If multiple deformation phases, domains, or lithologies are mixed, contours may show blended maxima that do not correspond to any single geological population.

> [!TIP]
> **Keep original data unchanged.** Clean or standardise measurements in a copy of the dataset, especially when converting legacy fields or harmonising strike and dip-direction conventions.

### *13.2. Common User Mistakes*

> [!WARNING]
> **No selected features.** Stereoplot plots selected features. If the selected layer contains data but no features are selected, the plot may be empty or incomplete.

> [!WARNING]
> **Using Identify instead of Select.** The QGIS Identify tool does not create selected features. Use QGIS selection tools or selection expressions.

> [!WARNING]
> **Mixed conventions.** Mixing strike, dip direction, right-hand-rule strike, and arbitrary strike in the same dataset can produce incorrect stereonet geometries.

> [!WARNING]
> **Invalid numeric ranges.** Check that dip and plunge values are between 0° and 90°, and that azimuthal values are between 0° and 360°.

> [!WARNING]
> **Over-interpreting contours.** Density contours depend on sample size, smoothing approach, and structural population selection. They should not be interpreted without considering sampling bias.

> [!WARNING]
> **Kinematic ambiguity.** Kinematic arrows depend on the encoded movement sense and the associated bearing plane. They should be used only where the structural measurement and kinematic interpretation are internally consistent.

### *13.3. Practical Structural Data Checklist*

Before plotting, check that:

- the correct QGIS layer is selected;
- the intended features are selected;
- structural fields are numeric and consistently named;
- planar measurements use a consistent convention;
- lineations have both trend and plunge values;
- combined datasets store the lineation and bearing plane on the same feature;
- kinematic classes are standardised where kinematic arrows are required;
- null, unknown, or uncertain measurements are clearly encoded;
- classification fields contain meaningful, non-random categories.

---

## 14. Troubleshooting

### *14.1. The plugin does not appear in QGIS*

Check that:

- the plugin folder is inside the active QGIS profile plugin directory;
- the folder is not nested inside another extracted ZIP folder;
- `metadata.txt` is present at the top level of the plugin folder;
- QGIS has been restarted after installation;
- the plugin is enabled in **Plugins > Manage and Install Plugins...**.

### *14.2. The plot is empty*

Possible causes:

- no features are selected;
- the wrong layer is selected;
- the selected features contain null structural measurements;
- field names are not recognised;
- filtering removes all features;
- the selected plotting mode does not match the available fields.

Suggested checks:

1. Clear any filter expression.
2. Select a small number of known valid features.
3. Confirm that the expected structural fields exist.
4. Manually set **Data to plot** in the settings dialog.
5. Try plotting without classification or contours first.

### *14.3. Great circles or poles look wrong*

Possible causes:

- strike is not stored using the expected convention;
- dip direction has been stored in a strike field;
- dip values are not numeric;
- azimuthal values include quadrant notation or text symbols;
- data were imported from legacy sources without harmonisation.

### *14.4. Kinematic arrows do not appear*

Check that:

- **Kinematics** is enabled;
- the selected dataset includes lineations;
- a valid kinematics field was selected;
- kinematic values are recognised;
- associated bearing-plane fields are populated;
- the selected plotting mode is **Lineations Only** or **Lineations with Bearing Planes** as appropriate.

### *14.5. Classification does not work as expected*

Check that:

- the classification field exists in the selected layer;
- the field contains populated values for selected features;
- the selected layer has not changed since settings were saved;
- categories have not been hidden in the interactive legend;
- aliases and real provider field names are not being confused.

### *14.6. Contours do not update*

Contours are recalculated from the visible data. If the contour pattern looks stale or unexpected:

1. check category visibility;
2. check the active filter expression;
3. disable and re-enable contours;
4. reopen the plot after updating settings;
5. verify that the visible dataset contains enough measurements.

---

## 15. Known Limitations

- Stereoplot is intended for exploratory structural data visualisation and first-pass analysis, not full structural modelling.
- Rose diagrams only represent azimuthal frequency and do not retain full 3D orientation information.
- Interactive stereonet selection is most appropriate for point-based stereonet elements and is not intended for rose diagrams or all great-circle workflows.
- Kinematic arrows are plotted only where valid lineation, bearing-plane, and kinematic-sense data are available.
- Automatic field detection relies on recognised field-name variants and may require manual override for highly customised datasets.
- Contour and girdle results can be sensitive to sample size, structural-domain mixing, and repeated measurements from the same locality.
- Style templates are project-level helper files and should be kept with the working QGIS project where reproducibility is required.

---

## 16. Credits and Contributors

### *16.1. WAXI/CET Redevelopment*

- **Julien Perret** — Centre for Exploration Targeting, University of Western Australia  
- **Mark Jessell** — Centre for Exploration Targeting, University of Western Australia

### *16.2. Foundational and Related Work*

- **Joe Kington** — `mplstereonet`, used for stereographic projection functionality.
- **Daniel Childs** — original QGIS stereonet plugin concepts and implementation lineage.

### *16.3. Related Projects*

Stereoplot is designed to work well with structural layers generated by the **GEOL-QMAPS** digital geological mapping solution, while remaining usable with independent QGIS structural datasets.

- GEOL-QMAPS repository: [https://github.com/swaxi/GEOL-QMAPS](https://github.com/swaxi/GEOL-QMAPS)
- Stereoplot repository: [https://github.com/swaxi/Stereoplot](https://github.com/swaxi/Stereoplot)

---

## 17. Licence and Citation

Stereoplot is distributed under the licence provided in the repository.

Repository:

```text
https://github.com/swaxi/Stereoplot
```

Suggested citation:

> *Perret, J. & Jessell, M.W., 2026. Stereoplot: an interactive QGIS plugin for stereographic projection and structural data visualisation. GitHub repository: [https://github.com/swaxi/Stereoplot](https://github.com/swaxi/Stereoplot).* 

If you use Stereoplot together with GEOL-QMAPS, please also cite the GEOL-QMAPS publication:

> *Perret, J., Jessell, M.W., Bétend, E., 2024. An open-source, QGIS-based solution for digital geological mapping: GEOL-QMAPS. Applied Computing and Geosciences 100197. [https://doi.org/10.1016/j.acags.2024.100197](https://doi.org/10.1016/j.acags.2024.100197).* 

---

## 18. Repository Media Used in this README

The following repository assets are referenced in this documentation:

| Asset | Purpose |
|---|---|
| `icon.png` | Plugin icon in the title line |
| `PluginButtons.PNG` | Toolbar buttons and plugin access |
| `SettingsWindow.PNG` | Settings dialog and quick-start workflow |
| `GreatCircles.PNG` | Stereonet great-circle visualisation |
| `RoseDiagrams.PNG` | Rose-diagram example |
| `Classification-InteractiveLegend-Styling.PNG` | Classification, interactive legend, and styling |
| `LineationsFilteringKinematics.PNG` | Filtering and kinematic-arrow workflow |
| `BestFitGirdle.PNG` | Best-fit girdle example |

