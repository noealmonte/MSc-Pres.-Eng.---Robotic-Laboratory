= Appendix

== Coordinate Frame Parameters
#figure(
  caption: [Summary Table of Manipulator Joint and Link Parameters],
  table(
    columns: (1fr, 1.5fr, 1.5fr, 1.5fr, 1.5fr),
    align: center,
    table.header([*Joint $i$*], [*$a_i$ [mm]*], [*$alpha_i$ [deg]*], [*$d_i$ [mm]*], [*$theta_i$ Range [deg]*]),
    [1], [0], [90], [135], [$-175$ to $+175$],
    [2], [135], [0], [0], [$-70$ to $+90$],
    [3], [38], [-90], [0], [$-135$ to $+70$],
    [4], [0], [90], [120], [$-170$ to $+170$],
    [5], [0], [-90], [0], [$-115$ to $+115$],
    [6], [0], [0], [70], [$-360$ to $+360$]
  )
)

== Video Demonstration Link
Video recording of at least 5 consecutive motion cycles for the repeatability evaluation:
- File / Link: `report/videos/meca500_repeatability_5cycles.mp4`
