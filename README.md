# Obuasi Healthcare Accessibility Mapper

This Week 1 GeoDev Lab project examines walking access to healthcare facilities in Obuasi, Ghana. It downloads openly available OpenStreetMap data, calculates 5-, 10- and 15-minute walking catchments, and produces an interactive web map.

## Spatial question

**Which populated communities within Obuasi Municipal and Obuasi East Municipal are located more than a 15-minute walk from a healthcare facility?**

## Study area

The study covers **Obuasi Municipal and Obuasi East Municipal** in the Ashanti Region of Ghana.

## Datasets

| Dataset | Use | Source |
|---|---|---|
| OpenStreetMap walking network | Pedestrian routing and travel-time calculation | [Geofabrik Ghana](https://download.geofabrik.de/africa/ghana.html) |
| OpenStreetMap healthcare facilities | Locations of hospitals, clinics, doctors and health centres | [OpenStreetMap](https://www.openstreetmap.org/) |
| Ghana administrative boundaries | Municipal boundary reference | [geoBoundaries/HDX](https://data.humdata.org/dataset/geoboundaries-admin-boundaries-for-ghana) |
| WorldPop 2025 population counts | Population exposure analysis in the next project phase | [WorldPop Ghana](https://hub.worldpop.org/geodata/summary?id=73551) |

OpenStreetMap data are retrieved directly in the script through OSMnx. Data coverage and accuracy may vary, so mapped facilities should be checked before the results are used for planning decisions.

## Method

1. Retrieve the boundaries of Obuasi Municipal and Obuasi East Municipal.
2. Download walkable roads and paths within the combined study area.
3. retrieve mapped healthcare facilities from OpenStreetMap.
4. Assign a walking time to each network edge using a speed of 4.8 km/h.
5. Snap healthcare facilities to their nearest network nodes.
6. Calculate 5-, 10- and 15-minute walking service areas.
7. Export an interactive HTML map and a CSV summary.

## Outputs

- `outputs/obuasi_healthcare_accessibility.html`
- `outputs/healthcare_facilities.csv`
- `outputs/analysis_summary.csv`

## Installation

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the analysis

```bash
python src/analysis.py
```

The first run may take several minutes because the road and facility data are downloaded from OpenStreetMap.

## Limitation and next phase

The current version evaluates geographic access to facilities recorded in OpenStreetMap. It does not assess opening hours, healthcare capacity, service quality, affordability or physical mobility constraints. The next phase will combine the 15-minute catchment with WorldPop data to estimate the number of residents outside the accessible area.

## Author

Developed for GeoDev Lab Africa, Cohort 1 (2026).

