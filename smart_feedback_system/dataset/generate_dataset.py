import csv
import os
import random

# Seed for reproducibility
random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, "college_feedback_dataset.csv")
SAMPLE_BULK_FILE = os.path.join(DATA_DIR, "sample_bulk_test.csv")

# Base domain examples categorized by language, sentiment, category, priority
CORE_EXAMPLES = [
    # --- TECHNICAL ---
    # English Negative
    ("The lab computer was not working and I couldn't complete my assignment.", "English", "Negative", "Infrastructure", "High"),
    ("The portal is dead again during course registration.", "English", "Negative", "Technical", "High"),
    ("Exam portal is not working and submission deadline is in one hour.", "English", "Negative", "Technical", "High"),
    ("Campus Wi-Fi disconnects repeatedly every 5 minutes in the hostel.", "English", "Negative", "Technical", "Medium"),
    ("LMS portal server crashed while uploading mid-term project files.", "English", "Negative", "Technical", "High"),
    ("ERP portal shows 504 gateway timeout whenever fees payment window opens.", "English", "Negative", "Technical", "High"),
    ("Student login credentials not accepted on the college mobile application.", "English", "Negative", "Technical", "Medium"),
    ("College website SSL certificate expired and browser warns unsafe site.", "English", "Negative", "Technical", "Medium"),
    ("Attendance tracking app is buggy and marks present students as absent.", "English", "Negative", "Technical", "High"),
    ("E-library database gives database error code 500 when accessing IEEE papers.", "English", "Negative", "Technical", "Medium"),
    
    # English Neutral
    ("The college portal UI was updated with a new blue theme.", "English", "Neutral", "Technical", "Low"),
    ("Wi-Fi network maintenance is scheduled for this Sunday morning.", "English", "Neutral", "Technical", "Low"),
    ("The ERP portal now requires two-factor authentication setup.", "English", "Neutral", "Technical", "Low"),
    ("LMS app received a new version update on Play Store.", "English", "Neutral", "Technical", "Low"),
    ("College server migration is ongoing this semester.", "English", "Neutral", "Technical", "Low"),
    
    # English Positive
    ("Campus Wi-Fi speed has improved significantly in the new engineering block.", "English", "Positive", "Technical", "Low"),
    ("The new college portal is very fast, clean and easy to navigate.", "English", "Positive", "Technical", "Low"),
    ("LMS portal allows seamless assignment submission without any glitch.", "English", "Positive", "Technical", "Low"),
    ("College IT helpdesk resolved my ERP login issue within 10 minutes.", "English", "Positive", "Technical", "Low"),
    ("Digital attendance system is super smooth and accurate.", "English", "Positive", "Technical", "Low"),

    # Hinglish Negative
    ("Sir, portal open nahi ho raha hai aur kal assignment submission hai.", "Hinglish", "Negative", "Technical", "High"),
    ("ERP site baar baar crash ho rahi hai fees pay karte waqt.", "Hinglish", "Negative", "Technical", "High"),
    ("Hostel Wi-Fi bilkul nahi chal raha do din se, bohot dikkat ho rahi hai.", "Hinglish", "Negative", "Technical", "High"),
    ("LMS pe quiz submit nahi ho raha, error aa raha hai urgently fix karo.", "Hinglish", "Negative", "Technical", "High"),
    ("Portal dead ho gaya hai, hall ticket download nahi ho paa rahi.", "Hinglish", "Negative", "Technical", "High"),
    ("College app bohot slow hai, attendance dekhne me 10 minute lagte hain.", "Hinglish", "Negative", "Technical", "Medium"),
    ("Wi-Fi password change kiya but kisi ka connect nahi ho raha.", "Hinglish", "Negative", "Technical", "Medium"),

    # Hinglish Neutral
    ("LMS portal ka design thoda change hua hai.", "Hinglish", "Neutral", "Technical", "Low"),
    ("College Wi-Fi timing normal chal raha hai abhi.", "Hinglish", "Neutral", "Technical", "Low"),
    ("Server maintenance ka notice mila hai kal ke liye.", "Hinglish", "Neutral", "Technical", "Low"),
    
    # Hinglish Positive
    ("Abhi portal ka speed bohot badhiya ho gaya hai.", "Hinglish", "Positive", "Technical", "Low"),
    ("IT team ne mera password issue turant solve kar diya, mast service.", "Hinglish", "Positive", "Technical", "Low"),
    ("Hostel me naya router lagaya hai, speed kafi achhi aa rahi hai.", "Hinglish", "Positive", "Technical", "Low"),

    # Tanglish Negative
    ("Lab lo Wi-Fi connection asalu ravatledu, speed chala slow undi.", "Tanglish", "Negative", "Technical", "High"),
    ("Sir portal open kavatledu, exam registration cheyalekapotunnanu.", "Tanglish", "Negative", "Technical", "High"),
    ("College ERP site crash ayyindi, fee payment fail ayyindi account nundi cut ayyindi.", "Tanglish", "Negative", "Technical", "High"),
    ("LMS login avvatledu, wrong password ani chupistundi urgently chudandi.", "Tanglish", "Negative", "Technical", "High"),
    ("Hostel block lo net connectivity assalu ledu, assignment cheyaleka potunnam.", "Tanglish", "Negative", "Technical", "High"),

    # Tanglish Neutral & Positive
    ("College Wi-Fi speed normal ga undi ippudu.", "Tanglish", "Neutral", "Technical", "Low"),
    ("New portal update vachindi, options maarayi.", "Tanglish", "Neutral", "Technical", "Low"),
    ("IT support chala fast ga system fix chesaru, chala bagundi.", "Tanglish", "Positive", "Technical", "Low"),
    ("Campus Wi-Fi ippudu super speed ga vastondi.", "Tanglish", "Positive", "Technical", "Low"),

    # Hindi & Telugu Script
    ("पोर्टल काम नहीं कर रहा है और सर्वर डाउन दिखा रहा है।", "Hindi", "Negative", "Technical", "High"),
    ("वाई-फाई की गति बहुत अच्छी और स्थिर है।", "Hindi", "Positive", "Technical", "Low"),
    ("కాలేజీ పోర్టల్ ఓపెన్ కావడం లేదు, ఎర్రర్ వస్తుంది.", "Telugu", "Negative", "Technical", "High"),
    ("క్యాంపస్ వైఫై చాలా వేగంగా పనిచేస్తోంది.", "Telugu", "Positive", "Technical", "Low"),

    # --- INFRASTRUCTURE ---
    # English Negative
    ("AC in seminar hall 3 is not working and it is suffocating during lectures.", "English", "Negative", "Infrastructure", "High"),
    ("Projector in Room 402 has severe flickering and bulb is damaged.", "English", "Negative", "Infrastructure", "Medium"),
    ("Chemistry lab exhaust fans are broken and dangerous fumes are accumulating.", "English", "Negative", "Infrastructure", "High"),
    ("Restrooms on the 2nd floor block B are extremely unhygienic and leaking.", "English", "Negative", "Infrastructure", "High"),
    ("Broken benches and desks in lecture hall 105 need immediate replacement.", "English", "Negative", "Infrastructure", "Medium"),
    ("Water purifier on 3rd floor is dispensing muddy brown water.", "English", "Negative", "Infrastructure", "High"),
    ("Library air conditioner has been broken for two weeks during peak summer.", "English", "Negative", "Infrastructure", "High"),
    ("Hostel mess food quality is completely deteriorated and unhygienic.", "English", "Negative", "Infrastructure", "High"),
    ("Elevator in main academic block got stuck between floors twice this week.", "English", "Negative", "Infrastructure", "High"),
    ("Computer lab chairs have broken backrests causing back pain.", "English", "Negative", "Infrastructure", "Low"),

    # English Neutral & Positive
    ("New desks have been installed in classroom 204.", "English", "Neutral", "Infrastructure", "Low"),
    ("Seminar hall seating capacity is around 250 students.", "English", "Neutral", "Infrastructure", "Low"),
    ("Campus cafeteria has average seating space during lunch hours.", "English", "Neutral", "Infrastructure", "Low"),
    ("The newly renovated auditorium acoustics and lighting are phenomenal.", "English", "Positive", "Infrastructure", "Low"),
    ("Central library has top-notch infrastructure, quiet cubicles and rich resources.", "English", "Positive", "Infrastructure", "Low"),
    ("Robotics and IoT lab is equipped with high-end modern workstations.", "English", "Positive", "Infrastructure", "Low"),
    ("Campus sports complex and indoor badminton court are exceptionally maintained.", "English", "Positive", "Infrastructure", "Low"),

    # Hinglish & Tanglish Infrastructure
    ("Room 201 ka fan aur light band hai, garmi me padhai nahi ho rahi.", "Hinglish", "Negative", "Infrastructure", "High"),
    ("Canteen ka khana bohot bekaar aur unhygienic ho gaya hai.", "Hinglish", "Negative", "Infrastructure", "High"),
    ("Lab ke computers bohot purane hain aur hang ho jaate hain.", "Hinglish", "Negative", "Infrastructure", "High"),
    ("Washroom me paani nahi aa raha hai subah se, urgent cleanliness chahiye.", "Hinglish", "Negative", "Infrastructure", "High"),
    ("Library ka reading room peaceful hai aur AC mast chal raha hai.", "Hinglish", "Positive", "Infrastructure", "Low"),
    ("Classroom lo bench lu virigi poyi unnai, kurchovadaniki ibbandi ga undi.", "Tanglish", "Negative", "Infrastructure", "High"),
    ("Water filter pani cheyatledu, drinking water problem undi block 2 lo.", "Tanglish", "Negative", "Infrastructure", "High"),
    ("Mess food chala worst ga undi, quality degrade ayyindi.", "Tanglish", "Negative", "Infrastructure", "High"),
    ("New computer lab chala spacious ga undi, AC kooda bagundi.", "Tanglish", "Positive", "Infrastructure", "Low"),

    # --- FACULTY ---
    # English Negative
    ("Faculty for DSP rushes through slides and never clarifies doubts in class.", "English", "Negative", "Faculty", "High"),
    ("The professor is consistently 25 minutes late and cancels lectures without notice.", "English", "Negative", "Faculty", "High"),
    ("Teacher behaves rudely whenever students ask conceptual questions.", "English", "Negative", "Faculty", "High"),
    ("Lab assistant refuses to help during practical experiments and talks harshly.", "English", "Negative", "Faculty", "Medium"),
    ("Subject teacher only reads from textbook without explaining underlying intuition.", "English", "Negative", "Faculty", "Medium"),
    ("Professor does not provide feedback on submitted lab records.", "English", "Negative", "Faculty", "Low"),
    
    # English Neutral & Positive
    ("The teacher covered unit 3 syllabus as scheduled.", "English", "Neutral", "Faculty", "Low"),
    ("Faculty follows standard textbook curriculum during classroom sessions.", "English", "Neutral", "Faculty", "Low"),
    ("Guest lecturer gave a 1 hour talk on cloud computing fundamentals.", "English", "Neutral", "Faculty", "Low"),
    ("Excellent teaching and lucid explanation of complex machine learning concepts.", "English", "Positive", "Faculty", "Low"),
    ("Professor Sharma is extraordinarily supportive, patient and inspiring.", "English", "Positive", "Faculty", "Low"),
    ("Our Data Structures professor conducts engaging hands-on coding sessions.", "English", "Positive", "Faculty", "Low"),
    ("Faculty clarifies every doubt patiently after class hours, great mentorship.", "English", "Positive", "Faculty", "Low"),

    # Hinglish & Tanglish Faculty
    ("Teacher bohot jaldi slides bhagate hain, kuch samajh nahi aata.", "Hinglish", "Negative", "Faculty", "High"),
    ("Sir class me doubt poocho toh gussa ho jaate hain aur daant dete hain.", "Hinglish", "Negative", "Faculty", "High"),
    ("Faculty hamesha late aate hain aur class jaldi chhod dete hain.", "Hinglish", "Negative", "Faculty", "Medium"),
    ("Maths sir bohot achha padhate hain, saare doubts clear kar dete hain.", "Hinglish", "Positive", "Faculty", "Low"),
    ("Physics mam teaching style is fantastic, real life examples deti hain.", "Hinglish", "Positive", "Faculty", "Low"),
    ("Faculty fast ga cheptunnaru, concept ardham kavatledu sir.", "Tanglish", "Negative", "Faculty", "High"),
    ("Sir doubs adigithe kopadutunnaru, correct ga explain cheyatledu.", "Tanglish", "Negative", "Faculty", "High"),
    ("Sir teaching super ga undi, real world examples tho neat ga explain chestaru.", "Tanglish", "Positive", "Faculty", "Low"),
    ("Lecturer chala friendly and helpful, doubts clear chestaru.", "Tanglish", "Positive", "Faculty", "Low"),

    # --- EXAMINATION ---
    # English Negative
    ("Mid-term exam schedule clashes with two core subject papers on same day.", "English", "Negative", "Examination", "High"),
    ("Evaluation of semester answer sheets was extremely unfair and biased.", "English", "Negative", "Examination", "High"),
    ("Hall tickets have spelling errors in student names and incorrect exam centers.", "English", "Negative", "Examination", "High"),
    ("End semester exam results delayed by over two months causing tension.", "English", "Negative", "Examination", "High"),
    ("Question paper contained out of syllabus questions worth 25 marks.", "English", "Negative", "Examination", "High"),
    ("Exam invigilator made excessive noise and disturbed concentration during paper.", "English", "Negative", "Examination", "Medium"),
    ("Revaluation fee is exorbitant and process takes too long to get updated marks.", "English", "Negative", "Examination", "Medium"),

    # English Neutral & Positive
    ("Mid term examination timetable was released on notice board today.", "English", "Neutral", "Examination", "Low"),
    ("The exam duration was 3 hours with 5 descriptive questions.", "English", "Neutral", "Examination", "Low"),
    ("Supplementary examination form submission deadline is next Friday.", "English", "Neutral", "Examination", "Low"),
    ("Examination cell conducted finals seamlessly with zero administrative hassle.", "English", "Positive", "Examination", "Low"),
    ("Question paper was very well balanced with fair difficulty distribution.", "English", "Positive", "Examination", "Low"),
    ("Semester results were declared promptly within 10 days, kudos exam department.", "English", "Positive", "Examination", "Low"),

    # Hinglish & Tanglish Examination
    ("Exam schedule bohot kharab hai, do tough paper ek hi din me rakh diye.", "Hinglish", "Negative", "Examination", "High"),
    ("Paper me 20 marks out of syllabus the, grace marks milne chahiye urgently.", "Hinglish", "Negative", "Examination", "High"),
    ("Exam results do mahine se pending hain, placement me problem ho rahi hai.", "Hinglish", "Negative", "Examination", "High"),
    ("Exam center seating arrangement normal tha.", "Hinglish", "Neutral", "Examination", "Low"),
    ("Exam evaluation fair tha aur time par results aa gaye.", "Hinglish", "Positive", "Examination", "Low"),
    ("Exam dates clash ayyayi, rendu major subjects same day unnayi urgently change cheyandi.", "Tanglish", "Negative", "Examination", "High"),
    ("Results inka raledu, chala delay chestunnaru exam branch vallu.", "Tanglish", "Negative", "Examination", "High"),
    ("Question paper lo out of syllabus questions vachayi 15 marks ki.", "Tanglish", "Negative", "Examination", "High"),
    ("Exam hall management chala neat ga conduct chesaru.", "Tanglish", "Positive", "Examination", "Low"),

    # --- COURSE ---
    # English Negative
    ("Course curriculum is severely outdated and lacks practical industry exposure.", "English", "Negative", "Course", "High"),
    ("Too many redundant assignments given in single week, unbearable workload.", "English", "Negative", "Course", "Medium"),
    ("Syllabus for Artificial Intelligence is purely theoretical without coding projects.", "English", "Negative", "Course", "High"),
    ("Textbook recommended by department is out of print and unavailable anywhere.", "English", "Negative", "Course", "Medium"),
    ("Elective subject options are extremely restricted and chosen without student consultation.", "English", "Negative", "Course", "Medium"),
    
    # English Neutral & Positive
    ("Sir class was okay, covered the usual unit 2 topics.", "English", "Neutral", "Course", "Low"),
    ("The course has 4 modules and 2 internal continuous assessments.", "English", "Neutral", "Course", "Low"),
    ("Course syllabus includes standard data structures and algorithmic complexity.", "English", "Neutral", "Course", "Low"),
    ("Curriculum has been brilliantly redesigned with modern industry AI tools and frameworks.", "English", "Positive", "Course", "Low"),
    ("Elective offerings on Cloud Architecture and DevOps are truly world-class.", "English", "Positive", "Course", "Low"),
    ("Hands-on mini projects in this course gave tremendous practical learning.", "English", "Positive", "Course", "Low"),

    # Hinglish & Tanglish Course
    ("Course syllabus bohot purana hai, modern tech stack bilkul nahi sikhate.", "Hinglish", "Negative", "Course", "High"),
    ("Assignments bohot zyada hain, self study ke liye bilkul time nahi mil raha.", "Hinglish", "Negative", "Course", "Medium"),
    ("Course structure theek thak hai, average content.", "Hinglish", "Neutral", "Course", "Low"),
    ("Elective subjects bohot practical aur informative hain, maza aa gaya.", "Hinglish", "Positive", "Course", "Low"),
    ("Syllabus outdated ga undi, present technologies cover cheyatledu.", "Tanglish", "Negative", "Course", "High"),
    ("Assignments load chala ekkuva aindi, deadline penchandi.", "Tanglish", "Negative", "Course", "Medium"),
    ("Course content standard ga undi.", "Tanglish", "Neutral", "Course", "Low"),
    ("Curriculum update chala bagundi, industry skills nerpistunnaru.", "Tanglish", "Positive", "Course", "Low"),

    # --- ADMINISTRATION ---
    # English Negative
    ("Administration office staff is exceptionally rude and delays scholarship verification.", "English", "Negative", "Administration", "High"),
    ("Bus transport coordinator not addressing overcrowded buses on route 14.", "English", "Negative", "Administration", "High"),
    ("Accounts department charged fine even though fees was paid before due date.", "English", "Negative", "Administration", "High"),
    ("Bonafide certificate application has been pending at registrar office for 3 weeks.", "English", "Negative", "Administration", "High"),
    ("Security guards misbehave with students at campus entry gates.", "English", "Negative", "Administration", "Medium"),
    ("Fee receipt generation failed and accounts staff asking to pay twice.", "English", "Negative", "Administration", "High"),
    ("Refund of caution deposit is delayed by six months without valid explanation.", "English", "Negative", "Administration", "High"),

    # English Neutral & Positive
    ("Fee counter operates between 9:30 AM and 3:30 PM on weekdays.", "English", "Neutral", "Administration", "Low"),
    ("Administrative circular issued regarding holiday on coming Monday.", "English", "Neutral", "Administration", "Low"),
    ("Transport fee slab details are displayed on the main notice counter.", "English", "Neutral", "Administration", "Low"),
    ("Scholarship processing was approved within 2 days with zero bureaucracy, thank you.", "English", "Positive", "Administration", "Low"),
    ("Administration staff at helpdesk was courteous, polite and extremely helpful.", "English", "Positive", "Administration", "Low"),
    ("College transport system is punctual, clean and safely managed.", "English", "Positive", "Administration", "Low"),
    ("ID card replacement was issued within 15 minutes smoothly.", "English", "Positive", "Administration", "Low"),

    # Hinglish & Tanglish Administration
    ("Admin office wale baat sunte hi nahi, scholarship form sign karne me 10 chakkar lagwaye.", "Hinglish", "Negative", "Administration", "High"),
    ("Accounts department me staff bohot batameezi se baat karta hai students se.", "Hinglish", "Negative", "Administration", "High"),
    ("Bus number 5 me bilkul jagah nahi hoti, khade hone ki bhi jagah nahi.", "Hinglish", "Negative", "Administration", "High"),
    ("Fee counter normal time pe open hua.", "Hinglish", "Neutral", "Administration", "Low"),
    ("Admin team ne bonafide certificate jaldi de diya bina kisi dikkat ke.", "Hinglish", "Positive", "Administration", "Low"),
    ("Admin office lo evaru respond avvatledu, scholarship sign kosam 10 days nundi tirugutunnam.", "Tanglish", "Negative", "Administration", "High"),
    ("College bus timing sarigga ledu, daily late ga vastondi route 12.", "Tanglish", "Negative", "Administration", "High"),
    ("Accounts section vallu fee payment refund ivvakunda delay chestunnaru.", "Tanglish", "Negative", "Administration", "High"),
    ("Office lo enquiry counter standard ga undi.", "Tanglish", "Neutral", "Administration", "Low"),
    ("Admin office staff chala quick ga help chesaru ID card issue lo.", "Tanglish", "Positive", "Administration", "Low")
]

# Variations and templates to expand dataset to 600+ realistic examples
EXPANSIONS = [
    # Variations for Technical
    ("College Wi-Fi speed in {location} is {sentiment_adj_neg}, cannot load any academic website.", "English", "Negative", "Technical", "High"),
    ("LMS upload speed for {course} is {sentiment_adj_pos}, works without error.", "English", "Positive", "Technical", "Low"),
    ("The {portal} portal is {sentiment_adj_neg} again, please resolve before tomorrow.", "English", "Negative", "Technical", "High"),
    ("Online attendance system status for {location} is recorded as per schedule.", "English", "Neutral", "Technical", "Low"),
    ("{location} lo net connectivity {sentiment_tang_neg}, classes follow avvalekapotunnam.", "Tanglish", "Negative", "Technical", "High"),
    ("{location} me server {sentiment_hing_neg}, jaldi theek karo.", "Hinglish", "Negative", "Technical", "High"),
    
    # Variations for Infrastructure
    ("{facility} in {location} is completely broken and {sentiment_adj_neg}.", "English", "Negative", "Infrastructure", "High"),
    ("{facility} in {location} is very well maintained and clean.", "English", "Positive", "Infrastructure", "Low"),
    ("The {facility} at {location} was opened for students today.", "English", "Neutral", "Infrastructure", "Low"),
    ("{facility} {sentiment_hing_neg} hai {location} me, bohot pareshani ho rahi hai.", "Hinglish", "Negative", "Infrastructure", "High"),
    ("{location} lo {facility} condition {sentiment_tang_neg}, repair cheyandi urgent ga.", "Tanglish", "Negative", "Infrastructure", "High"),

    # Variations for Faculty
    ("The faculty for {course} explains {sentiment_adj_pos} and motivates everyone.", "English", "Positive", "Faculty", "Low"),
    ("Faculty for {course} is not coming prepared and {sentiment_adj_neg}.", "English", "Negative", "Faculty", "High"),
    ("Lecture on {course} covered the syllabus topics as expected.", "English", "Neutral", "Faculty", "Low"),
    ("{course} sir chala {sentiment_tang_pos} ga cheptaru, doubts clear chestaru.", "Tanglish", "Positive", "Faculty", "Low"),
    ("{course} sir bohot {sentiment_hing_neg} padhate hain, samajh nahi aata.", "Hinglish", "Negative", "Faculty", "High"),

    # Variations for Examination
    ("Question paper for {course} examination was extremely {sentiment_adj_neg} and lengthy.", "English", "Negative", "Examination", "High"),
    ("The evaluation of {course} answer scripts was {sentiment_adj_pos} and transparent.", "English", "Positive", "Examination", "Low"),
    ("Examination schedule for {course} has been announced on the department board.", "English", "Neutral", "Examination", "Low"),
    ("{course} exam lo out of syllabus questions vachayi, chala {sentiment_tang_neg}.", "Tanglish", "Negative", "Examination", "High"),
    ("{course} exam results delay ho gaye, placement tension badh rahi hai.", "Hinglish", "Negative", "Examination", "High"),

    # Variations for Course
    ("The syllabus of {course} is {sentiment_adj_pos} and includes practical labs.", "English", "Positive", "Course", "Low"),
    ("Too many assignments for {course}, workload is {sentiment_adj_neg}.", "English", "Negative", "Course", "Medium"),
    ("Textbook syllabus for {course} covers introductory principles.", "English", "Neutral", "Course", "Low"),
    ("{course} syllabus chala useful and {sentiment_tang_pos} ga undi.", "Tanglish", "Positive", "Course", "Low"),
    ("{course} course content bohot outdated aur {sentiment_hing_neg} hai.", "Hinglish", "Negative", "Course", "High"),

    # Variations for Administration
    ("Administrative handling of {admin_issue} was {sentiment_adj_pos} and prompt.", "English", "Positive", "Administration", "Low"),
    ("Administration delays in resolving {admin_issue} are unacceptable and {sentiment_adj_neg}.", "English", "Negative", "Administration", "High"),
    ("Administration guidelines regarding {admin_issue} were circulated.", "English", "Neutral", "Administration", "Low"),
    ("{admin_issue} gurinchi admin staff {sentiment_tang_neg} ga behave chestunnaru.", "Tanglish", "Negative", "Administration", "High"),
    ("Admin office me {admin_issue} ke liye chakkar kaatne pad rahe hain, bohot {sentiment_hing_neg}.", "Hinglish", "Negative", "Administration", "High"),
]

VARS = {
    "location": ["Computer Lab 1", "Computer Lab 2", "Mechanical Block", "Electrical Lab", "Girls Hostel", "Boys Hostel Block B", "Main Library", "Floor 3 Seminar Hall", "ECE Dept"],
    "facility": ["Air Conditioner", "Water Dispenser", "Projector", "Restroom", "Sound System", "Lab Bench", "Ceiling Fan", "Lighting", "Elevator"],
    "course": ["Operating Systems", "Computer Networks", "Database Management", "Machine Learning", "Software Engineering", "Digital Signal Processing", "Data Structures", "Compiler Design"],
    "portal": ["student ERP", "examination fee", "e-library", "placement portal", "attendance app", "hall ticket"],
    "admin_issue": ["scholarship documents", "bus transport route", "fee concession", "bonafide certificate", "caution deposit refund", "hall ticket issuance", "ID card re-print"],
    "sentiment_adj_pos": ["exceptionally great", "wonderfully smooth", "highly engaging", "very prompt", "extremely helpful", "superb and clear", "impressive"],
    "sentiment_adj_neg": ["terrible and crashing", "unusable and broken", "horribly frustrating", "extremely unfair", "completely unhelpful", "poor quality"],
    "sentiment_hing_neg": ["bekaar", "kharab", "problematic", "slow", "down"],
    "sentiment_hing_pos": ["badhiya", "mast", "super", "achha"],
    "sentiment_tang_neg": ["worst ga undi", "pani cheyatledu", "chala slow", "problem aindi"],
    "sentiment_tang_pos": ["chala bagundi", "super ga undi", "neat ga undi"]
}

def generate_full_dataset():
    records = list(CORE_EXAMPLES)
    
    # Generate variations
    for template, lang, sentiment, category, priority in EXPANSIONS:
        for _ in range(16):
            text = template
            for var_key, var_list in VARS.items():
                if "{" + var_key + "}" in text:
                    text = text.replace("{" + var_key + "}", random.choice(var_list))
            records.append((text, lang, sentiment, category, priority))

    # Add more Hindi & Telugu scripts to ensure strong representation
    hindi_telugu_samples = [
        ("शिक्षक बहुत अच्छा पढ़ाते हैं और हर शंका का समाधान करते हैं।", "Hindi", "Positive", "Faculty", "Low"),
        ("लैब में कंप्यूटर ठीक से काम नहीं कर रहे हैं, असाइनमेंट अधूरा रह गया।", "Hindi", "Negative", "Infrastructure", "High"),
        ("परीक्षा समय सारिणी में दो कठिन विषयों की परीक्षा एक ही दिन है।", "Hindi", "Negative", "Examination", "High"),
        ("पुस्तकालय का वातावरण बहुत शांत और अध्ययन के लिए उत्तम है।", "Hindi", "Positive", "Infrastructure", "Low"),
        ("प्रशासन कार्यालय में छात्रवृत्ति सत्यापन में अनावश्यक देरी हो रही है।", "Hindi", "Negative", "Administration", "High"),
        ("पाठ्यक्रम आधुनिक उद्योग की आवश्यकताओं के अनुरूप बहुत उपयोगी है।", "Hindi", "Positive", "Course", "Low"),
        ("ఆచార్యుల బోధన చాలా స్పష్టంగా మరియు సులభంగా అర్థమవుతోంది.", "Telugu", "Positive", "Faculty", "Low"),
        ("ల్యాబ్ లో కంప్యూటర్లు పనిచేయడం లేదు, అసైన్‌మెంట్ పూర్తి కాలేదు.", "Telugu", "Negative", "Infrastructure", "High"),
        ("పరీక్షల టైమ్‌టేబుల్ విడుదలైనది, తేదీలు పరిశీలించగలరు.", "Telugu", "Neutral", "Examination", "Low"),
        ("హాస్టల్ మెస్ భోజనం నాణ్యత చాలా దారుణంగా ఉంది.", "Telugu", "Negative", "Infrastructure", "High"),
        ("స్కాలర్‌షిప్ పత్రాల ధృవీకరణ వెంటనే పూర్తయింది, ధన్యవాదాలు.", "Telugu", "Positive", "Administration", "Low"),
        ("కోర్సు సిలబస్ చాలా పాతదిగా ఉంది, మార్చవలసిన అవసరం ఉంది.", "Telugu", "Negative", "Course", "High")
    ]
    records.extend(hindi_telugu_samples)

    # Deduplicate and shuffle
    seen = set()
    unique_records = []
    for r in records:
        if r[0] not in seen:
            seen.add(r[0])
            unique_records.append(r)
    
    random.shuffle(unique_records)
    print(f"Total unique records generated: {len(unique_records)}")

    # Write to college_feedback_dataset.csv
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["feedback", "language", "sentiment", "category", "priority"])
        for r in unique_records:
            writer.writerow(r)
    print(f"Saved dataset to {OUTPUT_FILE}")

    # Write sample_bulk_test.csv for easy 1-click test upload in UI
    sample_test = [
        ("The lab computer was not working and I couldn't complete my assignment.", "English"),
        ("Sir, portal open nahi ho raha hai aur kal morning exam registration close ho jayegi.", "Hinglish"),
        ("Lab lo Wi-Fi connection asalu ravatledu, speed chala slow undi.", "Tanglish"),
        ("Professor explains all concepts very clearly and cleared all doubts.", "English"),
        ("Examination branch declared the mid term results promptly within 5 days.", "English"),
        ("Course curriculum is severely outdated and lacks practical coding projects.", "English"),
        ("Accounts department charged extra late fine unfairly, please refund.", "English"),
        ("Restrooms on 2nd floor are unhygienic and leaking water continuously.", "English"),
        ("Auditorium sound system and air conditioning are world class.", "English"),
        ("Teacher bohot jaldi slides bhagate hain, doubt poochne par gussa karte hain.", "Hinglish"),
        ("Classroom lo bench lu virigi poyi unnai, immediate ga replace cheyandi.", "Tanglish"),
        ("Canteen food is hygienic and prices are very reasonable.", "English"),
        ("Mid-term exam schedule clashes with two core subjects on Monday.", "English"),
        ("Digital attendance app marked present students as absent again.", "English"),
        ("Library has peaceful reading rooms and great collection of reference books.", "English")
    ]
    with open(SAMPLE_BULK_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["feedback"])
        for text, _ in sample_test:
            writer.writerow([text])
    print(f"Saved sample test CSV to {SAMPLE_BULK_FILE}")

if __name__ == "__main__":
    generate_full_dataset()
