# Offline gallery browser check

Chromium / Playwright was used to open the real self-contained gallery through a temporary local static server. The gallery uses embedded JPEG data, inline CSS/JavaScript and system fonts; the server is not needed by the downloaded HTML.

- First image and all six thumbnails displayed.
- Next-image button changed the selected picture, caption and active thumbnail.
- Native-pixel inspection toggled to Fit image; selecting another thumbnail reset the zoom.
- The electric view thumbnail selected the sixth native image correctly.
- Desktop full-page screenshot was opened and reviewed.
- A 390 × 844 mobile viewport screenshot was opened and reviewed; the picture, wrapped controls, three-column thumbnails and credits remained within the page width.
- The first static-server check produced only a missing-favicon 404, not a script failure. A self-contained inline SVG icon was added to prevent that unnecessary network request.

The Save image link points at the current embedded JPEG. Browser sandbox download permissions are controlled by the host viewer; the separate render ZIP is provided so downloads do not depend on that button.
