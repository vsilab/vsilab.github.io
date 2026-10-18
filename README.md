# VSI Lab website

Source for the Vision Systems and Intelligence Lab website, University of Arizona.

All content lives in plain text files in `_data/`. You edit those files directly on github.com. On every commit a GitHub Action regenerates the HTML pages (`index.html`, `research.html`, …) and commits them, and GitHub Pages publishes them within a minute or two. You do not need to install anything. Do not edit the `.html` files by hand; they are overwritten.

## One-time setup

1. Create a repository (for example `vsi-lab/vsi-lab.github.io`) and upload everything in this folder.
2. In the repository, open **Settings → Pages** and set **Source** to **Deploy from a branch**, branch **main**, folder **/ (root)** (the default).
3. Open the **Actions** tab and confirm that "Build site" finishes with a green check.

## Everyday updates

To edit a file on github.com, open it, click the pencil icon, make the change, and click **Commit changes**.

| Task | File | What to do |
|---|---|---|
| New paper accepted | `_data/publications.yml` | Copy any entry, paste it at the top, edit it, and add `status: to-appear`. It appears under **To Appear**. |
| Paper now published | `_data/publications.yml` | Delete the `status: to-appear` line and add `url:` with the DOI link. It moves to its own section. |
| New student | `_data/people.yml` | Add an entry under `members`. Upload the photo to `assets/people/` and write its file name after `photo:`. |
| Student graduates | `_data/people.yml` | Move the entry from `members` to `alumni`. Set `group`, `years`, and `now` (current position), and remove `photo`. |
| New service role or award | `_data/service.yml` | Add a line to the right group. |
| New course or program | `_data/teaching.yml` | Add an entry. |
| Research text, figures, sponsors | `_data/research.yml` | Edit the direction. Figures go in `assets/figures/`. |
| Bio, photo, CV link, contact | `_data/site.yml` | Edit the text. Upload `assets/cv.pdf` and set `cv: assets/cv.pdf` to show a CV link. |

Every file explains its own fields at the top.

## Format rules

- Keep the two-space indentation exactly as in the existing entries.
- If a value contains a colon, wrap it in double quotes, for example `title: "RVO-MIS: Robust Visual Odometry"`.
- If a build fails after a commit, the Actions tab shows the line with the problem. Fix it and commit again; the previous version of the site stays online until then.

## Photos and figures

- Portraits: a JPEG of about 640×800 pixels (4:5) keeps pages fast. The site shows photos in black and white and switches to color on hover.
- Research figures: a wide image on a white background. If a file is missing, the figure shows a quiet blank panel instead of a broken image.

## Preview on your own computer (optional)

```
pip install pyyaml
python3 _build/build.py --in-place
```

Then open `index.html`.

## Image credits (home-page overview figures)

The overview figures are drawn by `_build/figures/make_figures.py`. They use:

- Fundus photograph: Mikael Häggström, Wikimedia Commons, CC0 (distributed with scikit-image).
- Coffee photograph: Rachel Michetti, CC0; rocket launch photograph: SpaceX, public domain (both distributed with scikit-image).
- Brain template: MNI ICBM152 2009 nonlinear symmetric template, © McConnell Brain Imaging Centre, Montreal Neurological Institute; region coordinates from Seitzman et al. (2018). Both are distributed with nilearn.
- Robot photographs: Koh et al., "Selective Commitment for Language-Guided Object Retrieval under Partial Observability," Fig. 1.
- EB Garamond typeface: SIL Open Font License.
