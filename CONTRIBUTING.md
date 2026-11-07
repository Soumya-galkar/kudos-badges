\# Contributing to openSUSE Kudos Badges



Thank you for your interest in contributing to openSUSE Kudos Badges! Contributions are welcome. This guide explains how to submit new badge designs and their source files.



\## 1. Badge Design Requirements



\- Badge designs should follow the existing visual style and design guidelines in the repository.

\- Use the existing openSUSE Kudos color palette where appropriate.

\- Keep text readable and artwork consistent with the existing pixel-art aesthetic.

\- Each badge should have a clear purpose and measurable award criteria.

\- Use descriptive, lowercase filenames.



\## 2. Source Files (Required)



Every badge submission must include its original \*\*GIMP `.xcf` source file\*\*.



\- Keep the source file fully editable.

\- Organize artwork into clearly named layers.

\- Do not flatten the source image.

\- Keep different badge variations and tier elements in separate layers or layer groups.

\- Submit all relevant layers in a single `.xcf` file for each badge.



The source file is important because it allows maintainers and future contributors to modify badge artwork without recreating it from scratch.



Place source files in the `xcf/` directory.



\## 3. Badge Tiers



Some badges may have multiple achievement tiers depending on the contribution or activity being recognized.



The suggested tiers are:



| Tier | Multiplier |

|---|---:|

| Potato | 1x |

| Bronze | 10x |

| Silver | 100x |

| Gold | 1000x |



For example, badges recognizing YaST commits, rewards, submitted articles, or other measurable contributions could use these tiers.



When creating a multi-tier badge:



\- Keep all tier variations in one `.xcf` source file.

\- Use separate, clearly named layers or layer groups for each tier.

\- Make it easy to enable or disable individual tiers.

\- Ensure that each tier can be exported independently.



Not every badge needs to have multiple tiers. Use them when they make sense for the achievement being recognized.



\## 4. Required Exports



Along with the `.xcf` source file, contributors must provide a PNG export at \*\*1000px\*\*.



The expected repository structure is:



```text

xcf/

&#x20; badge-name.xcf



badge-name.png



previews/

&#x20; 800/

&#x20;   badge-name.png

&#x20; 200/

&#x20;   badge-name.png

```



The 1000px PNG is the main badge export. The smaller preview images should be generated using the repository's preview-generation script.



\## 5. Generating Previews



The repository provides a script to generate preview images:



\[generate-previews.sh](https://github.com/openSUSE/kudos-badges/blob/main/generate-previews.sh)



The script generates 800px and 200px versions from PNG files in the repository's root directory.



\### Prerequisites



Install ImageMagick and optipng.



On openSUSE:



```bash

sudo zypper install ImageMagick optipng

```



\### Run the script



From the repository root:



```bash

chmod +x generate-previews.sh

./generate-previews.sh

```



To regenerate all previews, including existing ones:



```bash

./generate-previews.sh --force

```



The generated files will be placed in:



\- `previews/800/`

\- `previews/200/`



Please commit the generated preview images along with the source file and main PNG export.



\## 6. Pull Request Checklist



Before submitting your pull request, make sure you have:



\- \[ ] Included the original `.xcf` source file in `xcf/`.

\- \[ ] Organized and named the source layers clearly.

\- \[ ] Included the 1000px PNG export.

\- \[ ] Generated the 800px and 200px previews using `generate-previews.sh`.

\- \[ ] Included all generated preview images.

\- \[ ] Provided a description of what the badge represents.

\- \[ ] Explained the award criteria, preferably with measurable thresholds.

\- \[ ] Checked that all exported images display correctly.



Thank you for helping celebrate the contributions of the openSUSE community!



💚 Happy contributing!

