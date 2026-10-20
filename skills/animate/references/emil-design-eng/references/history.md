# History and evidence

Stories and figures behind the rules in this skill, kept nearly verbatim from the vendor text.

## Vercel dashboard tabs (Motion shorthand under load)

At Vercel, the dashboard tab animation used Shared Layout Animations and dropped frames during page
loads. Switching to CSS animations (off main thread) fixed it. This is the case behind the rule
that Framer Motion's `x`/`y`/`scale` shorthands are not hardware-accelerated and that CSS animations
beat JS under load (see `performance-and-accessibility.md`).

## Sonner adoption

The Sonner principles come from building Sonner (13M+ weekly npm downloads). The figure is the
vendor's own claim, quoted as written; it was not measured on this box.

## Provenance

This skill was installed from emilkowalski/skills (author of Sonner and Vaul). The philosophy and
values are Emil Kowalski's; his course is [animations.dev](https://animations.dev/).
