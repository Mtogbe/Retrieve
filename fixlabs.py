import json

PATH = "data/labs.json"
TODAY = "2026-09-27"

# placeholder values that mean the field is really missing
MISSING = {"", "not found", "n/a", "none", "not applicable"}

# fields that hold links
URL_KEYS = ("website", "program_website", "source_url")

# working links, upgraded to the address the site actually lands on
URL_FIXES = {
    "http://www.cisa.umbc.edu/": "https://cisa.umbc.edu/",
    "http://coral-lab.umbc.edu/": "https://coral-lab.umbc.edu/",
    "http://iral.cs.umbc.edu/": "https://iral.cs.umbc.edu/",
    "http://vinjamurilab.cs.umbc.edu/": "https://vinjamurilab.cs.umbc.edu/",
    "http://esnet.cs.umbc.edu/": "https://esnet.cs.umbc.edu/",
    "http://www.umbc.edu/caspr/": "https://www2.umbc.edu/caspr/",
    "http://mlsp.umbc.edu/": "https://mlsp.umbc.edu/",
    "http://www.photonics.umbc.edu/": "https://photonics.umbc.edu/",
}

# links that load but show no real content
DEAD = {"https://eclipse.umbc.edu/"}

# websites set by id, for records whose link was wrong or dropped
ID_SITES = {
    "cs-003": "https://www.cremcenter.com/",
    "ee-003": "https://photonics.umbc.edu/",
}

# the 20 department overviews, listed so real programs added later survive
OVERVIEW_IDS = {"prog-%03d" % n for n in range(1, 21)}

# duplicates of people already listed as a lab lead, and archived labs
REMOVE_IDS = {
    "lab-105": "Farabaugh, archived",
    "lab-150": "MCAC, a facility rather than a lab",
    "ind-086": "Keke Chen, already listed as TAIC (cs-013)",
    "ind-017": "Govind Rao, already listed as Rao Lab / CAST (lab-139)",
}

# csee list page repeats labs already on the site, so it is not a useful link
CSEE_LIST = "https://www.csee.umbc.edu/research/research-labs/"

# biology research page is being retired, so point to each area page instead
BIO_OLD = "https://biology.umbc.edu/research/"
BIO_FACULTY = "https://biology.umbc.edu/faculty/"
BIO_AREAS = {
    "cell biology": "https://biology.umbc.edu/cell-biology/",
    "computational biology": "https://biology.umbc.edu/computational-biology/",
    "developmental biology / immunology": "https://biology.umbc.edu/developmental-biology-immunology/",
    "developmental biology & immunology": "https://biology.umbc.edu/developmental-biology-immunology/",
    "evolutionary biology": "https://biology.umbc.edu/evolutionary-biology/",
    "molecular biology / genetics": "https://biology.umbc.edu/molecular-biology-genetics/",
    "molecular biology & genetics": "https://biology.umbc.edu/molecular-biology-genetics/",
    "molecular biology": "https://biology.umbc.edu/molecular-biology-genetics/",
    "neuroscience": "https://biology.umbc.edu/neuroscience/",
    "plant biology": "https://biology.umbc.edu/plant-biology/",
}

# replace existing records by id, keeping fields not listed here
UPDATES = {
    "ind-085": {
        "website": "https://userpages.umbc.edu/~gobbert/",
        "contact_email": "gobbert@umbc.edu",
        "research_areas": ["computational modeling", "machine learning", "data science"],
        "description": "Scientific computing and parallel algorithms for computing clusters, machine learning for Big Data in science and engineering, numerical methods for partial differential equations, and applications in the life sciences, computational biology, and engineering.",
    },
    "lab-123": {
        "name": "Starz-Gaiano Laboratory",
        "website": "https://starzlab.umbc.edu/",
        "research_areas": ["cell biology", "developmental biology", "genetics"],
        "description": "Uses fruit flies (Drosophila) to find the genes and physical features of tissues that control cell migration, which matters for animal development and human disease.",
    },
    "lab-125": {
        "name": "The Vonhoff Lab",
        "website": "https://vonhofflab.umbc.edu/",
        "research_areas": ["neuroscience", "developmental biology", "genetics"],
        "description": "Uses the fruit fly Drosophila melanogaster to study neuroscience, from basic science to neurological diseases, including developmental mechanisms and aging-dependent degeneration. Students can pick a project or propose their own if it can be studied in the Drosophila nervous system.",
    },
    "lab-102": {
        "name": "Burns Arthropod Evolution (BAE) Lab",
        "website": "https://burnslab.umbc.edu/",
        "research_areas": ["evolutionary biology", "genetics", "computational biology"],
        "description": "Studies the evolutionary and ecological mechanisms behind sexual conflict in animal mating systems, especially in harvesters (daddy-longlegs). Combines genomic sequencing, functional morphology, bioinformatics, and cytological methods.",
    },
    "lab-104": {
        "name": "Elizondo Lab",
        "website": "https://elizondolab.umbc.edu/",
        "contact_email": "elizondolaboratory@gmail.com",
        "research_areas": ["immunology", "molecular biology", "genetics"],
        "description": "Studies how immune dysfunction breaks down tissue integrity and glucose homeostasis in diabetes using transgenic mouse models. Techniques include flow cytometry, CRISPR gene editing, single-cell and bulk RNA sequencing, qPCR, ELISA, and fluorescence microscopy.",
    },
    "lab-106": {
        "name": "Freeland Lab",
        "website": "https://freelandlab.umbc.edu/",
        "research_areas": ["evolutionary biology", "computational biology", "molecular biology"],
        "description": "Studies how and why evolution arrived at 20 amino acids for decoding genetic information. Uses computers to build and study amino acid structures beyond the standard genetic code, with a focus on astrobiology and the origin of life.",
    },
    "lab-107": {
        "name": "Gardner Lab",
        "website": "https://gardlab.umbc.edu/",
        "research_areas": ["molecular biology", "genetics"],
        "description": "Studies bacterial metabolism and physiology, using Cellvibrio japonicus to learn how microbes detect, degrade, and consume polysaccharides. Combines transcriptomics, proteomics, bacterial genetics, and biochemistry, and designs 3D printed devices for growth experiments.",
    },
    "lab-109": {
        "name": "Kann Lab",
        "website": "https://biology.umbc.edu/kann-lab/",
        "research_areas": ["computational biology", "genetics", "data science"],
        "accepting_students": "yes",
        "description": "Builds computational methods to study disease mutations and protein interactions, including databases of disease mutations mapped to protein domains. Undergraduate teams from biology and computer science build text-mining tools that extract mutations and protein interactions from biomedical literature. Some projects require no programming experience.",
    },
    "lab-110": {
        "name": "LeGates Lab",
        "website": "https://legateslab.umbc.edu/",
        "research_areas": ["neuroscience"],
        "description": "Studies how neurons integrate information to regulate behaviors related to depression, such as reward and cognitive function. Combines electrophysiology, imaging, and behavior in mice.",
    },
    "lab-111": {
        "name": "Leips Lab",
        "website": "https://leipslab.umbc.edu/",
        "research_areas": ["genetics", "evolutionary biology", "immunology"],
        "description": "Studies the genetic basis of natural variation in aging using Drosophila melanogaster. Uses genetic mapping, genomics, and functional approaches. Current projects focus on age-related changes in immunity, reproduction, and physical performance.",
    },
    "lab-112": {
        "name": "Weihong Lin Lab",
        "website": "https://linlab.umbc.edu/",
        "research_areas": ["neuroscience", "cell biology"],
        "description": "Studies chemical sensory systems in the nose, including detection of e-cigarette flavors and sensory dysfunction from chemical exposure. Uses genetically modified mice, calcium imaging, electrophysiological recordings, immunolabeling, and behavioral assays.",
    },
    "lab-113": {
        "name": "Lobo Lab",
        "website": "https://lobolab.umbc.edu/",
        "research_areas": ["computational biology", "computational modeling", "developmental biology"],
        "description": "Reverse engineers the mechanisms that control biological growth and form. Combines computational methods, mathematical models, and bioinformatics with bench experiments to study development, regeneration, cancer, and synthetic biology.",
    },
    "lab-114": {
        "name": "Lohr Lab",
        "website": "https://userpages.umbc.edu/~blohr/",
        "research_areas": ["evolutionary biology", "neuroscience"],
        "description": "Studies bird hearing and song. Projects include how far songbirds can detect and recognize songs in noise, Grasshopper Sparrow song variation and breeding behavior, sexual selection and birdsong, and comparative hearing across bird species.",
    },
    "lab-116": {
        "name": "Mendelson Lab",
        "website": "https://biology.umbc.edu/pending-deletion/mendelson-lab/",
        "research_areas": ["evolutionary biology", "genetics"],
        "description": "Studies the causes and consequences of behavioral evolution using North American freshwater fish called darters. Projects cover mate choice, male breeding color, reproductive isolation, and phylogenies built from molecular markers.",
    },
    "lab-117": {
        "name": "Miller Lab",
        "website": "https://biology.umbc.edu/miller-lab/",
        "research_areas": ["developmental biology", "cell biology", "molecular biology", "genetics", "evolutionary biology", "plant biology"],
        "description": "Uses the green alga Volvox carteri to study how cells differentiate and how that evolved. Projects cover how asymmetric cell divisions are regulated and how the somatic cell fate is maintained.",
    },
    "lab-119": {
        "name": "Omland Lab",
        "website": "https://omlandlab.umbc.edu/",
        "research_areas": ["evolutionary biology"],
        "accepting_students": "yes",
        "description": "Studies avian evolution, ecology, behavior, and conservation, with a focus on New World orioles. Recent work covers female coloration, female song, and the Puerto Rican Oriole. Prospective students are invited to email about the Puerto Rico work or related projects.",
    },
    "lab-120": {
        "name": "Padmanabhan Lab",
        "website": "https://padmanabhanlab.umbc.edu/",
        "research_areas": ["cell biology", "molecular biology", "immunology"],
        "description": "Studies how normal cells become cancerous, how cancer cells grow, evade the immune system, and metastasize, and how to build more effective cancer therapies. Uses molecular, cellular, and organismic tools.",
    },
    "lab-121": {
        "name": "Robinson Lab",
        "website": "https://robinsonlab.umbc.edu/",
        "research_areas": ["cell biology", "molecular biology", "neuroscience"],
        "description": "Studies phototransduction, how light in the environment becomes a biological signal.",
    },
    "lab-122": {
        "name": "Schreier Laboratory",
        "website": "https://imet.usmd.edu/lab/schreier-laboratory",
        "research_areas": ["molecular biology"],
        "description": "Studies nitrogen and sulfur cycles in marine recirculating aquaculture systems and nitrogen fixation in the gut of a wood-eating catfish. Based at the Institute of Marine and Environmental Technology in Baltimore.",
    },
    "lab-124": {
        "name": "Sutton Lab",
        "website": "https://suttonlab.umbc.edu/",
        "research_areas": ["neuroscience", "molecular biology", "cell biology"],
        "description": "Studies G protein coupled receptor (GPCR) signaling in the brain and how disruptions contribute to neuropsychiatric and neurodegenerative disease. Uses behavioral phenotyping, proteomics, imaging, and cell-based assays.",
    },
    "lab-126": {
        "name": "The Walker Lab at UMBC",
        "website": "https://www.ndwalkerlab.com/",
        "research_areas": ["cell biology", "molecular biology"],
        "description": "Studies how exosomes reprogram cells to drive breast cancer metastasis, with projects on metastatic initiation, breast cancer dormancy in bone marrow, and tissue repair and regeneration.",
    },
    "lab-127": {
        "name": "Cronin Lab",
        "website": "https://biology.umbc.edu/archived/cronin-lab/",
        "research_areas": ["neuroscience", "evolutionary biology"],
        "description": "Studies the visual physiology of invertebrates, especially mantis shrimp, including color vision, polarized-light signals, and the molecular genetics of opsins. Also studies how many other animals evolved vision suited to their environments.",
    },
}

# brand new records
NEW = [
    {
        "id": "lab-149",
        "name": "CIRC - Center for Interdisciplinary Research and Consulting",
        "pi_name": "Dr. Nagaraj K. Neerchal",
        "website": "https://circ.umbc.edu/",
        "department": "Mathematics and Statistics",
        "research_areas": ["statistics", "computational modeling"],
        "description": "A math and statistics consulting service run by the Department of Mathematics and Statistics. Supports interdisciplinary research in the biological sciences, engineering, and social sciences, and gives students consulting experience as research assistants.",
        "contact_email": "nagaraj@math.umbc.edu",
    },
    {
        "id": "lab-151",
        "name": "Lu Research Group",
        "pi_name": "Ye Lu",
        "website": "https://yelu.umbc.edu/",
        "department": "Mechanical Engineering",
        "research_areas": ["computational modeling", "materials science", "manufacturing", "machine learning"],
        "description": "Computational mechanics and materials science, including reduced order modeling and data-driven methods for high-performance computing, multi-scale modeling of materials and additive manufacturing, fracture mechanics, and digital image correlation.",
        "contact_email": "yelu@umbc.edu",
    },
    {
        "id": "prog-021",
        "name": "Human-Centered Computing Program",
        "pi_name": "Graduate Program Director",
        "website": "https://hcc.umbc.edu/",
        "department": "Information Systems",
        "research_areas": ["human-computer interaction"],
        "description": "Studies how humans interact with technology, in the Department of Information Systems. Offers study at the undergraduate, masters, and PhD level. Enrolled undergraduates can email the Graduate Program Director to join a mailing list for HCC events, internships, and job opportunities.",
        "contact_email": "hcc-gpd@umbc.edu",
        "record_type": "research_program",
    },
]

DEFAULTS = {
    "accepting_students": "unknown",
    "research_program": "not found",
    "program_website": "not found",
    "record_type": "lab",
    "last_checked": TODAY,
}


def has_value(value):
    # true if the field holds real text
    return isinstance(value, str) and value.strip().lower() not in MISSING


def has_link(value):
    # true if the field holds a real web address
    return has_value(value) and value.strip().startswith("http")


def bio_page(lab):
    # biology area page that fits this record, or the faculty directory
    area = str(lab.get("research_program") or "").strip().lower()
    return BIO_AREAS.get(area, BIO_FACULTY)


with open(PATH, encoding="utf-8") as f:
    labs = json.load(f)

kept = []
for lab in labs:
    lab_id = lab.get("id")

    # drop department overviews, since they have no contact and repeat listed faculty
    if lab.get("record_type") == "research_program" and lab_id in OVERVIEW_IDS:
        print("removed overview", lab_id, "-", lab.get("name"))
        continue

    # drop duplicates and archived labs
    if lab_id in REMOVE_IDS:
        print("removed", lab_id, "-", REMOVE_IDS[lab_id])
        continue

    # drop records with no email and no website of their own
    if not has_value(lab.get("contact_email")) and not has_link(lab.get("website")) and lab_id not in ID_SITES:
        print("removed", lab_id, "-", lab.get("name"))
        continue

    for key in URL_KEYS:
        url = lab.get(key)
        if url in URL_FIXES:
            print("fixed", lab_id, key, url, "->", URL_FIXES[url])
            lab[key] = URL_FIXES[url]
        elif url == BIO_OLD:
            lab[key] = bio_page(lab)
            print("fixed", lab_id, key, url, "->", lab[key])

    if lab_id in ID_SITES and lab.get("website") != ID_SITES[lab_id]:
        print("fixed", lab_id, "website", lab.get("website"), "->", ID_SITES[lab_id])
        lab["website"] = ID_SITES[lab_id]

    if lab.get("website") in DEAD:
        print("dropped placeholder website for", lab_id, lab["website"])
        del lab["website"]

    if lab.get("program_website") == CSEE_LIST:
        del lab["program_website"]
        print("dropped csee list link from program_website for", lab_id)

    # swap in the real lab data, only printing when something changes
    if lab_id in UPDATES:
        new = dict(UPDATES[lab_id])
        new["source_url"] = new["website"]
        if any(lab.get(k) != v for k, v in new.items()):
            lab.update(new)
            lab["last_checked"] = TODAY
            print("updated", lab_id, "-", lab["name"])

    kept.append(lab)

# add new records, or refresh them if an earlier run already added them
have = {lab.get("id"): lab for lab in kept}
for rec in NEW:
    new = dict(rec)
    new["source_url"] = new["website"]
    old = have.get(rec["id"])
    if old is None:
        full = dict(DEFAULTS)
        full.update(new)
        kept.append(full)
        print("added", rec["id"], "-", rec["name"])
    elif any(old.get(k) != v for k, v in new.items()):
        old.update(new)
        old["last_checked"] = TODAY
        print("updated", rec["id"], "-", rec["name"])

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(kept, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(len(labs), "records before,", len(kept), "after")