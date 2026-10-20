# Copy motion from a screen recording, frame by frame

Read this when the user wants an animation to "move like app X" and can record app X on their phone, or when
our own animation "feels off" and a recording of it can be compared. It is the method used to copy a native
iOS app's motion into a web app: measure the recording frame by frame, rebuild the motion from the numbers,
then measure our copy the same way before asking for a phone check. Eyeballing a video at full speed gets
the feel wrong; every value here comes from a measured frame. The incidents behind the lessons are in
`history.md` ("Copying motion from recordings").

## Steps

1. **Get a screen recording from the phone.** A still screenshot cannot show motion. An iPhone records
   at 3x: 1179 px wide is 393 pt. Before measuring any press, ask whether iOS "Show Touches" was on (see
   the lessons). When our version feels off, ask for a recording of OURS and compare the two the same way.
2. **Get ffmpeg without installing it** when `ffmpeg` is missing:

   ```bash
   FF=$(uvx --with imageio-ffmpeg python -c "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())")
   ```

3. **Extract the native frames, never a resampled copy.** Keep every frame exactly as recorded, with its
   own timestamp (`pts_time` from `showinfo`):

   ```bash
   mkdir -p frames
   "$FF" -i rec.mov -vf "scale=393:-1,showinfo" -fps_mode passthrough frames/%04d.png 2> showinfo.log
   grep -o "pts_time:[0-9.]*" showinfo.log      # one timestamp per frame
   ```

   Scale to 393 px wide (1 px = 1 pt) for positions and sizes; extract a second set at full resolution
   for colours.
4. **Find the moments.** Compute the mean absolute difference per screen region (header, middle, bottom)
   between consecutive frames; the spikes are where something moves.
5. **Measure per frame.** Take the bounding box of what changed against a rest frame: its size gives the
   scale, its position gives the origin. Take the brightest pixel in a box for a text or rim colour, and
   sample a fill mid-body, not near rounded ends (the corner radius shortens the column). Contrast-boost a
   few frames to see subtle things (whether the page really dimmed, whether a small overshoot happened).
6. **Turn the numbers into motion.**
   - Origin of a scale: with `left(s) = xo + (left_final - xo) * s` on two frames, solve for `xo`.
   - A spring: fit damping, frequency and start scale to the measured points (a small grid search), then
     sample the fitted curve into a CSS `linear()` easing (33-37 points).
   - An irregular path (an icon that flies past its spot and settles): use the measured points as
     keyframes with `linear` between them, played with WAAPI.
   - Write the measured timeline as a table (phase, theirs, ours) next to the code, so the next pass
     compares numbers, not impressions.
7. **Measure our copy the same way before asking for a phone check.** In a headless browser, sample
   computed styles every animation frame (a `requestAnimationFrame` loop reading `getComputedStyle`) and
   compare the numbers row by row with the recording's table. Only then ask the user to feel it on the
   phone, and record which items are matched headless but not yet felt on a device.

Done when: our sampled timeline matches the recording's table within a frame or two, and the user has
confirmed the feel on the phone.

## Lessons (each one cost a round with the user)

- **Use the original frames, never a resampled 60 fps copy.** Resampling with `fps=60` duplicates frames
  and smears a one-frame snap into what looks like a 70 ms fade, so the copy comes out wrong.
- **Measure position, size and colour per frame**, not by watching. A guessed overshoot, origin or
  colour is the part the user notices.
- **The grey circle with a light rim in a recording is iOS's show-touches marker, not part of the app.**
  A circle that follows the finger, appears in one frame and vanishes on release is the screen recorder
  marking the touch. Never copy it.
- **Measure our version the same way before asking for a phone check.** Headless numbers catch most
  mismatches without spending the user's time.
- **DOM checks can lie about paint.** An element can be present and opaque in the DOM and still be off
  screen. When something "vanishes" on a phone, record per-frame paint (a CDP screencast) and read its
  `getBoundingClientRect()` every frame.
- **Anything that slides in from off-screen must be inside a box that clips sideways**
  (`overflow-x: clip` on its container; vertical overflow can stay visible). While the element sits past
  the edge the page is wider than the screen, mobile browsers grow the layout viewport to fit (the phone
  zooms the page out), and every fixed bar moves with it.
- **Start an animation triggered by a DOM observer one `requestAnimationFrame` later.** A
  `MutationObserver` can fire inside a view transition's DOM update; starting an off-screen animation
  there made Chrome abort the transition (`Transition was aborted because of invalid state`).
- **Animate individual properties (`scale`, `filter`, `opacity`) when the element is positioned with a
  `transform`.** A `transform` keyframe overrides a centring translate.
- **A `filter: blur()` on a big shadowed card drops frames on an iPhone.** Leave blur off large surfaces
  even when the recording seems to show it.
- **When the user says "it should be like in the video", re-measure the native frames** instead of
  tuning the current version; the first reading was usually of the wrong mechanism (a cross-fade where
  the app actually unrolled a panel).
- **A headless sampler must not block the tap.** With Playwright, an `evaluate_handle` sampler followed
  by a later `tap()` queues the tap behind the sampling promise; start sampling from an in-page
  `pointerdown` listener instead.
