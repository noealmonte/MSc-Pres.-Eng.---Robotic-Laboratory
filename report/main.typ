#import "template_victor_francey.typ": *

#show: project.with(
  title: "Precision Industrial Robot Manipulation (Meca500)",
  subtitle: "Control and Automation — Robotics Laboratory",
  subsubtitle: "Master of Science in Precision Engineering",
  authors: (
    "Noé Almonte",
    "Florian Nuoffer"
  ),
  class_name: "Group Robotics",
  professor: "Gabriel Grüner",
  //assistant: "Tizian Bürgi",
  academic_year: "2026-2027",
  lieux: "Bern",
  date: [4 January 2027],
  table_matiere: true,
  liste_fig: false,
  liste_tab: false,
  bib: false
)

#include "contenu/1_Introduction.typ"
#include "contenu/2_Session1_Jogging_Safety.typ"
#include "contenu/3_Session2_Kinematics.typ"
#include "contenu/4_Session3_Repeatability.typ"
#include "contenu/5_Conclusion.typ"
#include "contenu/annexe.typ"

#bibliography("bibliographie.bib")
