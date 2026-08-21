"""Dump every unique affiliation with its current country classification (or Other)."""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Comprehensive country hint list (case-insensitive substring matching)
COUNTRY_HINTS = [
    ("USA", [
        # Top universities
        "MIT", "Massachusetts Institute of Technology", "Stanford", "CMU", "Carnegie Mellon",
        "Berkeley", "UCLA", "University of California, Los Angeles",
        "UCSD", "UC San Diego", "University of California, San Diego",
        "UC Berkeley", "UCR", "UC Riverside", "University of California, Riverside",
        "UC Irvine", "UCI", "University of California, Irvine",
        "UC Santa", "University of California, Santa", "UC Davis", "University of California, Davis",
        "University of California", "UC Merced",
        "Harvard", "Princeton", "Cornell", "Columbia University", "Yale", "Caltech",
        "California Institute of Technology", "Georgia Tech", "Georgia Institute of Technology",
        "University of Michigan", "Michigan State", "University of Illinois", "Illinois Institute of Technology",
        "University of Texas", "UT Austin", "Texas A&M", "University of Washington",
        "University of Pennsylvania", "Penn State", "Northwestern University", "NYU",
        "New York University", "Boston University", "Boston College", "Purdue", "Rutgers",
        "University of Maryland", "University of Wisconsin", "University of Minnesota",
        "Notre Dame", "Johns Hopkins", "JHU", "Duke University", "University of Virginia",
        "University of North Carolina", "North Carolina State", "University of Florida",
        "Florida State", "Arizona State", "University of Arizona", "University of Colorado",
        "Colorado State", "University of Utah", "Utah State", "Worcester Polytechnic",
        "Rensselaer", "RPI ", "University of Rochester", "Stony Brook", "University at Buffalo",
        "Buffalo State", "University of Iowa", "Iowa State", "University of Tennessee",
        "Vanderbilt", "Rice University", "USC", "University of Southern California",
        "Oregon State", "University of Oregon", "Drexel", "Lehigh", "Northeastern University",
        "Brown University", "Dartmouth", "Wesleyan", "Tufts", "Syracuse",
        "George Mason", "George Washington", "Georgetown",
        "Stevens Institute", "Binghamton", "University of Pittsburgh", "Pitt",
        "Carnegie Mellon", "University of Connecticut", "UConn", "Lehigh",
        "University of Nevada", "UNR", "Brigham Young", "BYU", "University of Utah",
        "University of Delaware", "University of Georgia", "University of Arkansas",
        "Auburn University", "Mississippi State", "University of Mississippi", "LSU",
        "University of Louisville", "University of Kentucky", "University of Cincinnati",
        "Ohio State", "Case Western", "University of Akron", "Kent State",
        "University of Houston", "Texas Tech", "Baylor University", "SMU",
        "University of New Hampshire", "University of Vermont", "University of Maine",
        "University of Massachusetts", "UMass", "Amherst College", "Williams College",
        "Swarthmore", "Haverford", "Smith College", "Wellesley", "Barnard",
        "Allen Institute for AI", "Allen Institute for Artificial Intelligence",
        "Lehigh University", "Drew University", "Princeton",
        # Government / national labs
        "Army Research", "ARL", "NASA", "JPL", "Jet Propulsion", "Naval Research",
        "Naval Postgraduate", "Air Force", "Sandia", "Oak Ridge", "Lawrence Livermore",
        "Argonne", "Lawrence Berkeley", "Brookhaven", "Los Alamos", "NIST", "DARPA",
        "NIH", "Pacific Northwest National Lab",
        # Industry
        "Meta", "Facebook", "Google", "DeepMind", "Microsoft", "Apple", "NVIDIA", "Nvidia",
        "Amazon", "Tesla", "Boston Dynamics", "Toyota Research", "TRI",
        "Samsung Research America", "Robotics and AI Institute", "RAI Institute",
        "Apptronik", "Figure AI", "Skydio", "Anduril", "Open AI", "OpenAI",
        "Motional", "Waymo", "Cruise", "Argo AI", "Nuro", "Zoox", "Aurora",
        "Disney Research", "Woods Hole", "Nokia Bell Labs", "Bell Labs",
        "MITRE", "RAND", "Lincoln Lab", "MIT Lincoln", "Aerospace Corporation",
        "iRobot", "Anyscale", "Anthropic", "Hugging Face", "Lyft", "Uber", "Airbnb",
        "JP Morgan", "Bloomberg", "Adobe", "Salesforce",
    ]),
    ("China", [
        # Top
        "Tsinghua", "Peking University", "Beihang", "Fudan", "Zhejiang University",
        "Shanghai Jiao Tong", "Shanghai Jiaotong", "ShangHai Jiao Tong",
        "Sun Yat-Sen", "Sun Yat-sen", "Xi'an Jiaotong", "Xi’an Jiaotong",
        "Wuhan University", "Sichuan University", "Harbin Institute", "Harbin Engineering",
        "USTC", "University of Science and Technology of China",
        "University of Electronic Science and Technology", "UESTC",
        "SUSTech", "Southern University of Science and Technology",
        "ShanghaiTech", "Tongji", "Nanjing University", "Renmin", "Nankai", "Naikai", "Tianjin",
        "Dalian", "Chongqing", "Northeastern University, China",
        "Northeastern University (Shenyang)", "South China University", "East China University",
        "East China Normal", "Central South University", "Hunan University", "Jilin University",
        "Lanzhou", "Yunnan", "Chinese Academy of Sciences", "CAS,", "CASIA",
        "Institute of Automation", "China University", "Beijing Institute",
        "Beijing University", "Beijing Normal", "Beijing Jiaotong", "Beijing Forestry",
        "Beijing Aeronautics", "Capital Normal", "Capital Medical",
        "Shanghai University", "Shanghai Maritime", "Shenzhen University", "Shenzhen Institute",
        "Hangzhou Dianzi", "Hangzhou University", "Westlake", "Great Bay University",
        "Huazhong", "Southeast University", "Shandong University", "Guangdong University",
        "Xiamen University", "Jiangnan", "Hefei University", "Taiyuan",
        "Inner Mongolia", "Soochow", "Northwest A&F", "Northwest Polytechnical",
        "Northwestern Polytechnical", "Zhengzhou University", "Information Engineering University",
        "Southwest University", "Ocean University of China", "Xidian", "Xi’an University",
        "Xi'an University", "University of Macau", "Macau University", "Macao Polytechnic",
        "Polytechnic University of Hong Kong", "Tianjin University",
        # Companies
        "Huawei", "Tencent", "Baidu", "Alibaba", "DJI",
        "Chang'an", "Chang’an", "PLA ",
        "National University of Defense Technology",
        "ZTE", "Li Auto", "LiAuto", "BYD", "Geely", "NIO", "Xpeng", "Pony.ai", "AutoX",
        "Hikvision", "Horizon Robotics", "Midea Group", "Midea ", "ByteDance", "PICO ",
        "WeRide", "Momenta", "DeepRoute", "SenseTime", "Sense Time",
        "Meituan", "JD.com", "JD Logistics", "Xiaomi", "Lenovo", "OPPO", "Vivo",
        "TencentAI", "Galaxy Robotics", "Unitree", "AgiBot", "Galbot",
        # Cities
        "Beijing", "Shanghai", "Shenzhen", "Hangzhou", "Wuhan", "Chengdu",
        "Nanjing", "Suzhou", "Hefei", "Qingdao", "Jinan", "Changsha", "Kunming",
        "Nanchang", "Xi'an, China", "Xi’an, China",
    ]),
    # Hong Kong / Macau merged into China
    ("China-HK-Macau", [
        "Hong Kong", "HKUST", "HKU ", "PolyU", "CityU", "CUHK",
        "Centre for Transformative Garment Production",
        "Macau", "Macao",
    ]),
    ("Taiwan", [
        "Taiwan", "Yang Ming Chiao Tung", "National Taiwan", "NCTU", "NTU,Taiwan",
        "National Cheng Kung", "NCKU", "Tsing Hua",
        "Taipei", "Hsinchu",
    ]),
    ("South Korea", [
        # Top
        "KAIST", "POSTECH", "Seoul National", "Korea University", "Yonsei",
        "Hanyang", "Sungkyunkwan", "SungKyunKwan", "UNIST", "Ulsan National Institute",
        "Pohang", "Korea Advanced", "GIST", "DGIST",
        "Gwangju Institute of Science", "Daegu Gyeongbuk Institute",
        "Korea Institute of Science and Technology",
        "Chungbuk", "Chungnam", "Pusan", "Kyungpook", "Inha", "Ajou", "Sogang",
        "Konkuk", "Hongik", "Gyeongsang", "Chonnam", "Kyung Hee", "KyungHee",
        "Gachon", "Yeungnam", "Kookmin", "Keimyung", "Kumoh", "Jeonbuk",
        "Ewha", "Chung-Ang", "University of Seoul", "Sejong University",
        "Korea National", "Korea Maritime", "Korea Aerospace",
        "Korea Polytechnic", "Korea Research Institute of Ships",
        "Korea Institute of Industrial Technology", "Korea Institute of Machinery",
        "KRISO", "KITECH", "KIMM", "KIST",
        # Companies
        "Hyundai", "Kia ", "Samsung", "LG ", "Neuromeka", "ETRI",
        # removed bare "KAI " — too prone to false positives (e.g. "Naikai", "Tokai")
        "Hanwha", "Doosan", "KEPCO", "Naver", "Kakao",
        "Republic of Korea", "Korea, ", " Korea ",
    ]),
    ("Japan", [
        "Tokyo", "Kyoto", "Osaka", "Kyushu", "Hokkaido", "Tohoku", "Nagoya",
        "Tsukuba", "Waseda", "Keio", "JAXA", "AIST", "Tokai", "Toyohashi",
        "Ritsumeikan", "Doshisha", "Kobe", "Hiroshima", "Okayama",
        "Ibaraki", "Saitama", "Chiba", "Yokohama", "Kanazawa", "Niigata",
        "OMRON", "Honda", "Sony", "Toyota", "Mitsubishi", "Hitachi",
        "Panasonic", "Fanuc", "Denso", "Bridgestone", "Tokyo Institute",
        "Tokyo University", "Japan", "Chuo University", "Nara Institute",
        "NAIST", "Tokyo University of Agriculture",
        "National Institute of Advanced Industrial Science",
    ]),
    ("Singapore", [
        "Singapore", "NUS", "Nanyang Technological", "NanyangTechnological",
        "NTU,", "Agency for Science", "ASTAR", "A*STAR",
    ]),
    ("Germany", [
        # Cities
        "Munich", "München", "Berlin", "Karlsruhe", "Stuttgart", "Aachen",
        "Hamburg", "Heidelberg", "Bonn", "Freiburg", "Tubingen", "Tübingen",
        "Darmstadt", "Bremen", "Bielefeld", "Bochum", "Dortmund", "Dresden",
        "Erlangen", "Frankfurt", "Goettingen", "Göttingen", "Hannover",
        "Hanover", "Kiel", "Leipzig", "Magdeburg", "Mannheim", "Marburg",
        "Mainz", "Muenster", "Münster", "Nuremberg", "Nürnberg", "Saarland",
        "Ulm", "Wuerzburg", "Würzburg", "Weimar", "Cologne", "Köln",
        "Paderborn", "Braunschweig", "Konstanz", "Chemnitz",
        # Universities
        "RWTH", "TUM", "TU Berlin", "TU Munich", "TU Darmstadt", "TU Dresden",
        "Technische Universität", "Technical University of Munich",
        "Bundeswehr München", "Universität der Bundeswehr",
        # Industry / labs
        "DLR", "Fraunhofer", "Max Planck", "Bosch", "Siemens", "BMW",
        "Mercedes", "Volkswagen", "VW Group", "Audi", "Continental", "Aumovio",
        "Daimler", "Porsche", "Carl Zeiss", "Helmholtz", "Schaeffler", "ZF Friedrichshafen",
        "Germany",
    ]),
    ("UK", [
        "Oxford", "Cambridge", "Imperial College", "UCL ", "University College London",
        "King's College", "King’s College", "Edinburgh", "Manchester", "Bristol",
        "Warwick", "Sheffield", "Leeds", "Birmingham", "Glasgow", "Liverpool",
        "Southampton", "Surrey", "Sussex", "York", "Loughborough",
        "Nottingham", "Lancaster", "Durham", "Reading", "Strathclyde",
        "Aberdeen", "St Andrews", "Heriot-Watt", "Bath", "Queen Mary",
        "Essex", "Cardiff", "Newcastle", "United Kingdom", "Plymouth",
        "Bournemouth", "Brunel", "Westminster", "Lincoln", "Hertfordshire",
        "Leicester", "Kent", "Exeter", "Royal Holloway", "Goldsmiths",
        "London School of Economics", "LSE,", "Open University,",
    ]),
    ("France", [
        "Paris", "Sorbonne", "INRIA", "Inria", "CNRS", "Cnrs", "ENS ", "ENSTA",
        "École", "Ecole", "Lyon", "Marseille", "Toulouse", "Grenoble",
        "Lille", "Nice", "Bordeaux", "Strasbourg", "Nantes", "Rennes",
        "Montpellier", "Versailles", "Compiegne", "Compiègne",
        "LAAS", "IRISA", "Mines ", "Centrale", "PSL", "France",
        "Institut Polytechnique", "Polytechnique de Paris", "Sciences Po",
        "Université Paris", "Univ Rennes", "Univ Lyon", "Université de",
    ]),
    ("Italy", [
        "Milano", "Milan", "Turin", "Torino", "Roma", "Rome", "Naples",
        "Napoli", "Padova", "Padua", "Pisa", "Bologna", "Firenze",
        "Florence", "Genova", "Genoa", "Trento", "Trieste", "Bari",
        "Catania", "Palermo", "Sicily", "Italy", "Politecnico",
        "Sapienza", "Tor Vergata", "Sant'Anna", "Sant’Anna",
        "Istituto Italiano", "Italian Institute of Technology", "IIT ",
        "Verona", "Siena", "Ferrara", "Brescia", "Modena", "Salento",
        "Salerno", "Calabria", "Università",
    ]),
    ("Switzerland", [
        "ETH ", "EPFL", "Zurich", "Lausanne", "Geneva", "Bern", "Basel",
        "Idiap", "Switzerland", "Università della Svizzera",
        "Schweiz", "Suisse", "St. Gallen", "Lugano",
    ]),
    ("Netherlands", [
        "Delft", "TU Delft", "Eindhoven", "Twente", "Wageningen",
        "Leiden", "Utrecht", "Rotterdam", "Amsterdam", "Groningen",
        "Maastricht", "Netherlands", "Holland",
        "Vrije Universiteit Amsterdam", "VU Amsterdam",
        "Tilburg", "Nijmegen",
    ]),
    ("Spain", [
        "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", "Granada",
        "Bilbao", "Salamanca", "Murcia", "Tenerife", "La Laguna",
        "Spain", "Catalunya", "Catalonia", "Universidad de", "Universitat de",
        "Alcalá", "Alcala", "Pablo de Olavide", "Pablo De Olavide",
        "Carlos III", "UC3M", "Pompeu Fabra",
    ]),
    ("Sweden", [
        "KTH", "Stockholm", "Uppsala", "Lund", "Chalmers", "Linköping",
        "Linkoping", "Gothenburg", "Sweden", "Luleå", "Lulea", "Örebro",
        "Orebro", "Halmstad", "Mid Sweden", "Skövde", "Skovde", "Karlstad",
    ]),
    ("Norway", [
        "Oslo", "Trondheim", "NTNU", "SINTEF", "Norway", "Bergen", "Tromsø",
        "Tromso", "Norwegian University", "Stavanger", "Agder",
    ]),
    ("Denmark", [
        "Copenhagen", "Aalborg", "Aarhus", "DTU", "Southern Denmark",
        "Denmark", "Roskilde",
    ]),
    ("Finland", [
        "Aalto", "Helsinki", "Tampere", "Turku", "Oulu", "Finland",
        "Jyväskylä", "Jyvaskyla", "VTT,",
    ]),
    ("Belgium", [
        "KU Leuven", "Ghent", "Antwerp", "Antwerpen", "Brussels", "Liege",
        "Liège", "Belgium", "Vrije Universiteit Brussel", "VUB,", "ULB",
        "ULiège", "UCLouvain", "Mons,",
    ]),
    ("Austria", [
        "Vienna", "Wien", "Graz", "Linz", "Innsbruck", "Salzburg", "Austria",
        "TU Wien", "JKU", "Klagenfurt", "Steyr",
    ]),
    ("Czech", [
        "Prague", "Praha", "Czech Technical", "CTU ", "Brno", "Czech",
        "Czechia", "Ostrava", "Olomouc",
    ]),
    ("Poland", [
        "Warsaw", "Warszawa", "Krakow", "Cracow", "Wrocław", "Wroclaw",
        "Gdansk", "Gdańsk", "Poznan", "Poznań", "Poland", "Lodz", "Łódź",
        "Lublin", "Katowice", "Polski", "Polska",
    ]),
    ("Portugal", [
        "Lisbon", "Lisboa", "Porto", "Coimbra", "Portugal", "Aveiro",
        "Universidade de", "IST,", "Técnico Lisboa",
    ]),
    ("Greece", [
        "Athens", "Thessaloniki", "Patras", "Crete", "Greece", "Aristotle",
        "Heraklion", "Ioannina",
    ]),
    ("Ireland", [
        "Dublin", "Trinity College", "Cork", "Galway", "Ireland", "Limerick",
        "Maynooth",
    ]),
    ("Croatia", [
        "Zagreb", "Croatia", "Hrvatska", "Rijeka", "Split,", "Pula",
    ]),
    ("Luxembourg", [
        "Luxembourg",
    ]),
    ("Hungary", [
        "Budapest", "Hungary", "Hungaria", "Debrecen", "Szeged", "Pécs",
    ]),
    ("Romania", [
        "Bucharest", "București", "Cluj", "Romania", "Iași", "Iasi",
        "Timișoara", "Timisoara",
    ]),
    ("Slovenia", [
        "Ljubljana", "Slovenia", "Maribor",
    ]),
    ("Slovakia", [
        "Bratislava", "Slovakia", "Košice", "Kosice",
    ]),
    ("Estonia", [
        "Tartu", "Tallinn", "Estonia",
    ]),
    ("Latvia", [
        "Riga", "Latvia",
    ]),
    ("Lithuania", [
        "Vilnius", "Lithuania", "Kaunas",
    ]),
    ("Russia", [
        "Moscow", "Saint Petersburg", "St. Petersburg", "Russia", "Skolkovo",
        "Novosibirsk", "Kazan", "Yekaterinburg",
    ]),
    ("Ukraine", [
        "Kyiv", "Kiev", "Lviv", "Kharkiv", "Ukraine",
    ]),
    ("Serbia", [
        "Belgrade", "Beograd", "Serbia", "Novi Sad", "Niš", "Nis,",
    ]),
    ("Canada", [
        "Toronto", "Waterloo", "McGill", "UBC ", "British Columbia",
        "Alberta", "Calgary", "Montreal", "Ottawa", "Western University",
        "Concordia", "Simon Fraser", "Queen's University", "Queen’s University",
        "Dalhousie", "Manitoba", "Saskatchewan", "York University", "Carleton",
        "Canada", "McMaster", "Université Laval", "Laval University", "MDA Space",
        "Memorial University", "University of Guelph", "Polytechnique Montreal",
        "Polytechnique Montréal",
    ]),
    ("Australia", [
        "Sydney", "Melbourne", "Queensland", "Monash", "ANU ",
        "Australian National", "UNSW", "New South Wales", "Adelaide",
        "Western Australia", "Macquarie", "RMIT", "Curtin",
        "Australia", "CSIRO", "QUT", "Wollongong", "James Cook",
        "Bond University", "Deakin", "Griffith University", "La Trobe",
    ]),
    ("New Zealand", [
        "Auckland", "Otago", "Canterbury", "Victoria University of Wellington",
        "New Zealand", "Massey",
    ]),
    ("India", [
        "IIT ", "IISc", "Indian Institute", "Delhi University",
        "University of Delhi", "Mumbai", "Bangalore", "Bengaluru",
        "Chennai", "Madras", "Kolkata", "Calcutta", "Hyderabad",
        "Pune", "Kanpur", "Kharagpur", "Roorkee", "Guwahati", "India",
        "BITS Pilani", "Manipal", "Anna University", "Jadavpur", "VIT,",
    ]),
    ("Israel", [
        "Technion", "Tel Aviv", "Hebrew University", "Weizmann", "Bar-Ilan",
        "Ben-Gurion", "Israel", "Reichman",
    ]),
    ("UAE", [
        "Khalifa", "Mohamed Bin Zayed", "MBZUAI", "UAE", "Emirates",
        "Abu Dhabi", "Dubai", "Technology Innovation Institute", "TII -",
    ]),
    ("Saudi Arabia", [
        "KAUST", "King Abdullah", "King Saud", "Riyadh", "Jeddah",
        "Saudi", "Dhahran", "KFUPM",
    ]),
    ("Qatar", [
        "Qatar", "Hamad bin Khalifa", "Doha,",
    ]),
    ("Turkey", [
        "Istanbul", "Ankara", "Bilkent", "Koç", "Sabanci", "METU",
        "Turkey", "Türkiye", "Bogazici", "Boğaziçi",
        "Middle East Technical",
    ]),
    ("Iran", [
        "Tehran", "Sharif", "Iran", "Isfahan", "Shiraz", "Tabriz",
        "Amirkabir",
    ]),
    ("Pakistan", [
        "Pakistan", "Lahore", "NUST,", "LUMS,", "Islamabad",
    ]),
    ("Brazil", [
        "São Paulo", "Sao Paulo", "Rio de Janeiro", "Brazil", "Brasil",
        "Brasilia", "USP,", "UFRJ", "UFMG", "UFRGS", "UFSC", "Unicamp",
        "Pontifícia Universidade",
    ]),
    ("Mexico", [
        "UNAM", "Mexico", "México", "Monterrey", "Guadalajara",
        "Tecnológico", "ITESM", "CINVESTAV",
    ]),
    ("Argentina", [
        "Buenos Aires", "Argentina", "Cordoba",
    ]),
    ("Chile", [
        "Santiago", "Chile", "Pontificia Universidad Católica de Chile",
    ]),
    ("South Africa", [
        "Cape Town", "Johannesburg", "Stellenbosch", "South Africa",
        "Pretoria", "Witwatersrand",
    ]),
    ("Egypt", [
        "Cairo", "Egypt", "Alexandria", "AUC,",
    ]),
    ("Philippines", [
        "Mindanao", "Philippines", "Manila",
    ]),
    ("Vietnam", [
        "Vietnam", "Hanoi", "Ho Chi Minh", "VinUni", "VNU,",
    ]),
    ("Thailand", [
        "Thailand", "Chulalongkorn", "Mahidol", "Bangkok",
    ]),
    ("Malaysia", [
        "Malaysia", "Kuala Lumpur", "USM,", "UTM,",
    ]),
    ("Indonesia", [
        "Indonesia", "Jakarta", "ITB,", "UI,",
    ]),
]


def country_for(aff: str) -> str:
    s = aff.lower()
    for country, hints in COUNTRY_HINTS:
        for h in hints:
            if h.lower() in s:
                # HK/Macau folded into China per request
                return "China" if country == "China-HK-Macau" else country
    return "Other"


def main():
    root = Path(__file__).resolve().parent.parent
    data = json.loads((root / "output" / "papers.json").read_text(encoding="utf-8"))
    papers = data["papers"]

    aff_counter = Counter()
    for p in papers:
        for a in p["authors"]:
            aff_counter[a["aff"]] += 1

    classified = []
    for aff, n in aff_counter.most_common():
        classified.append({"aff": aff, "count": n, "country": country_for(aff)})

    # Output: full list
    out = root / "classification" / "affiliations_classified.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(classified, ensure_ascii=False, indent=1), encoding="utf-8")

    # Stats
    total_authors = sum(aff_counter.values())
    other = [c for c in classified if c["country"] == "Other"]
    other_authors = sum(c["count"] for c in other)
    print(f"unique affiliations: {len(classified)}")
    print(f"total author slots: {total_authors}")
    print(f"Other: {len(other)} unique affs, {other_authors} author slots ({other_authors/total_authors*100:.1f}%)")
    print(f"\nTop 30 still-Other affiliations:")
    for c in other[:30]:
        print(f"  {c['count']:5d}  {c['aff']}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
