#let project(
  title: "",
  subtitle: "",
  subsubtitle: "",
  authors: (),
  logo: "BFH_logo.png",
  logo_right: "Unibe_logo.png",
  header_text: "",
  class_name: "",
  professor: "",
  //assistant: "",
  academic_year: "",
  lieux: "",
  date: "",
  table_matiere: true,
  liste_fig: true,
  liste_tab: true,
  bib: true,
  body
) = {

  set document(author: authors, title: title)
  
  set text(font: "New Computer Modern", lang: "en")

  show math.equation: set text(weight: 400)
  set math.equation(numbering: "(1)", number-align: right, supplement: none)

  show ref: it => {
    let el = it.element

    if el != none and (el.func() == math.equation or (el.func() == figure and el.kind == math.equation)) {
      [(#it)]
    } else {
      it
    }
  }
  
  show figure.where(kind: table): set figure.caption(position: top)
  
  show raw.where(block: true): block.with(
    width: 100%,
    fill: luma(240),
    inset: 10pt,
    radius: 5pt,
  )

  show raw.where(block: false): box.with(
    fill: luma(240),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 2pt,
  )
  show figure.where(kind: table): set figure(supplement: [Table])
  show figure.where(kind: image): set figure(supplement: [Figure])
  set heading(numbering: "1.1") 

  v(0.6fr)
  
  // En-tête avec les deux logos
  grid(
    columns: (1fr, 1fr),
    align(start + top)[
      #if logo != none {
        image(logo, width: 40%)
      }
    ],
    align(end + top)[
      #if logo_right != none {
        image(logo_right, width: 40%)
      }
    ],
  )

  if header_text != none {
    v(1.2em)
    align(start)[
      #text(1.2em, fill: luma(60))[#header_text]
    ]
  }

  /*
  v(7fr)

  text(2em, weight: 700, title)
  v(0.3fr)
  text(1.5em, weight: 100, subtitle)
  v(0.9fr)
  text(1.2em, weight: 100, subsubtitle)
  v(2fr)
  */
  v(4fr) // Réduit au lieu de 7fr pour remonter le bloc titre

  text(2em, weight: 700, title)
  v(0.3fr)
  text(1.4em, weight: 400, fill: luma(60), subtitle)
  v(0.4fr)
  text(1.1em, style: "italic", fill: luma(80), subsubtitle)
  
  v(0.4fr)
  line(length: 100%, stroke: 0.5pt + luma(150)) // Optionnel : ligne de séparation
  v(2.5fr)
  pad(
    left: 0%,
    right: 0%,
    top: 0.6em,
    grid(
      columns: (auto, 1fr),
      gutter: 1.2em,
      align(start)[*Group*],
      align(start)[#class_name],
      align(start)[*Students*],
      align(start)[#authors.join(", ")],
      align(start)[*Lecturer*],
      align(start)[#professor],
      //align(start)[*Assistant*],
      //align(start)[#assistant],
      align(start)[*Academic year*],
      align(start)[#academic_year],
    )
  )
  v(3fr)
  align(right + bottom)[
    #text(weight: 300)[#lieux, #date]
  ]
  // v(1fr)
  pagebreak()
  set page(
    margin: (top: 2.5cm, bottom: 2.5cm, left: 2cm, right: 2cm),
    header: [
      #set text(size: 9pt) 
      #grid(
        columns: (1fr, 1fr),
        align(left)[#title],
        align(right)[#authors.join(", ")]
      )
      #v(0.1em)
      #line(length: 100%, stroke: 0.5pt)
    ],
    
    footer: context [
      #set text(size: 9pt)
      #line(length: 100%, stroke: 0.5pt)
      #v(0.1em)
      #align(right)[
        #counter(page).display()
      ]
    ]
  )
  set page(numbering: "i", number-align: end)
  counter(page).update(1)
  if table_matiere {
    outline(title: "Table of contents", indent: auto)
    pagebreak()
  }
  if liste_fig {
    outline(
      title: "List of figures",
      target: figure.where(kind: image),
    )
    pagebreak()
  }
  if liste_tab {
    outline(
      title: "List of tables",
      target: figure.where(kind: table),
    )
    pagebreak()
  }
  set page(numbering: "1", number-align: end)
  counter(page).update(1)
  set par(justify: true)
  body
  if bib {
    bibliography("bibliographie.bib", style: "ieee", title: "Références") 
  }
}