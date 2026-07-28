# lasso elasticnet

LASSO و Elastic Net هر دو برای موقعیتی ساخته شده‌اند که شما **feature زیاد** دارید، sample نسبتاً کم است، و predictorها با هم correlated هستند. دقیقاً مثل پروژه شما: N حدود ۱۰۳، اما بیش از هزار digital indicator از eye, stylus, keyboard, voice و taskهای مختلف.

مسئله اصلی این است: اگر همه featureها را با regression معمولی وارد کنیم، مدل می‌تواند در همان sample ظاهراً خوب کار کند، ولی در داده جدید خراب شود. همان چیزی که در ارائه شما دیده شد: pooled model با ۲۳ predictor درون‌نمونه‌ای R² بالا داشت، اما cross-validation تقریباً صفر شد. این یعنی مدل بخشی از noise همان sample را یاد گرفته بود، نه یک الگوی پایدار.

### **ایده پایه: regression معمولی چه می‌کند؟**

در linear regression معمولی می‌گوییم:

PedsQL = β0 + β1X1 + β2X2 + β3X3 + ... + error

مدل تلاش می‌کند coefficientها را طوری پیدا کند که خطای پیش‌بینی کم شود. یعنی مجموع خطاهای مربعی را minimize می‌کند.

مشکل: وقتی featureها زیادند، مدل می‌تواند coefficientهای بزرگ و ناپایدار بسازد. مثلاً اگر چند feature eye-tracking خیلی شبیه هم باشند، regression ممکن است به یکی coefficient مثبت بزرگ بدهد، به دیگری coefficient منفی بزرگ، فقط برای fit بهتر روی همین sample. این از نظر علمی خطرناک است.

### **LASSO چیست؟**

LASSO همان regression است، اما یک جریمه اضافه می‌کند. این جریمه مدل را مجبور می‌کند coefficientها را کوچک کند، و بعضی را دقیقاً صفر کند.

فرمول مفهومی‌اش این است:

loss = prediction error + λ × sum(|β|)

یعنی مدل دو هدف دارد:

اول، PedsQL را خوب توضیح بدهد.

دوم، coefficientهای زیادی و بزرگ نسازد.

λ یا lambda شدت جریمه است.

اگر λ کوچک باشد، مدل شبیه regression معمولی می‌شود.

اگر λ بزرگ باشد، مدل سخت‌گیر می‌شود و featureهای زیادی را صفر می‌کند.

پس LASSO یک کار خیلی مفید انجام می‌دهد:

**feature selection**

یعنی اگر ۱۰۰ feature داشته باشید، ممکن است فقط ۴ تا را نگه دارد و coefficient بقیه را صفر کند.

مثال ساده:

فرض کنیم در Eye × Numeracy این featureها را داریم:

gaze_path_displacement

fixation_entropy

saccade_velocity

gaze_position_y

pupil_variability

LASSO ممکن است بگوید:

gaze_path_displacement   -2.8

fixation_entropy          0.0

saccade_velocity          0.0

gaze_position_y          -1.1

pupil_variability         0.0

یعنی فقط دو feature را انتخاب کرده است.

تفسیر:

gaze_path_displacement و gaze_position_y بعد از کنترل بقیه featureها بیشترین اطلاعات را برای PedsQL دارند؛ بقیه featureها در این مدل contribution کافی ندارند.

### **چرا LASSO برای پروژه شما جذاب است؟**

چون شما feature زیاد دارید و نمی‌خواهید stepwise ناپایدار باشد. LASSO به جای اینکه مثل stepwise یکی‌یکی feature اضافه و حذف کند، همه featureها را همزمان می‌بیند و با جریمه‌کردن coefficientها یک مدل sparse می‌سازد.

Sparse یعنی مدل با تعداد کمی predictor.

این برای N=103 مهم است، چون نمی‌توانید مثلاً ۵۰ feature را با خیال راحت در یک regression معمولی بگذارید.

### **اما مشکل LASSO چیست؟**

مشکل اصلی LASSO وقتی است که featureها با هم correlation بالا دارند.

مثلاً فرض کنید این سه feature خیلی شبیه هم‌اند:

fixation_entropy_mean

fixation_entropy_std

saccade_entropy_mean

هر سه یک خانواده رفتاری را نشان می‌دهند: irregularity یا unpredictability در eye movement.

اگر این‌ها highly correlated باشند، LASSO ممکن است فقط یکی را انتخاب کند و بقیه را صفر کند. اما اینکه کدام یکی انتخاب شود، ممکن است تصادفی و sample-dependent باشد.

در یک bootstrap:

fixation_entropy_mean انتخاب می‌شود

در bootstrap بعدی:

fixation_entropy_std انتخاب می‌شود

در bootstrap سوم:

saccade_entropy_mean انتخاب می‌شود

پس پیام علمی شاید این باشد که «eye-movement irregularity مهم است»، اما LASSO ممکن است feature دقیق را ناپایدار نشان دهد.

این برای پروژه شما مهم است، چون digital features اغلب خانواده‌ای و correlated هستند: gaze position features، gaze velocity features، saccade features، touch pressure features، timing features و غیره.

### **Elastic Net چیست؟**

Elastic Net ترکیبی از LASSO و Ridge است.

LASSO جریمه‌ای دارد که بعضی coefficientها را صفر می‌کند.

Ridge جریمه‌ای دارد که coefficientها را کوچک می‌کند ولی معمولاً صفر نمی‌کند.

Elastic Net هر دو را با هم ترکیب می‌کند.

فرمول مفهومی:

loss = prediction error + λ × [α × LASSO penalty + (1 - α) × Ridge penalty]

در اینجا دو پارامتر مهم داریم:

λ یعنی شدت کلی جریمه.

α یعنی ترکیب LASSO و Ridge.

اگر:

α = 1

Elastic Net تقریباً همان LASSO است.

اگر:

α = 0

تقریباً Ridge است.

اگر:

α = 0.5

بین این دو است.

### **Ridge چه فرقی دارد؟**

Ridge coefficientها را کوچک می‌کند، اما معمولاً صفر نمی‌کند.

مثلاً:

gaze_path_displacement   -1.4

fixation_entropy         -0.9

saccade_velocity         -0.5

gaze_position_y          -0.7

pupil_variability        -0.2

همه را نگه می‌دارد، ولی effectها را shrink می‌کند.

Ridge برای prediction خوب است، مخصوصاً وقتی featureها correlated هستند. اما feature selection واضح نمی‌دهد، چون همه چیز در مدل می‌ماند.

LASSO feature selection واضح می‌دهد، اما با correlated features ناپایدار می‌شود.

Elastic Net وسط این دو است:

**هم selection می‌کند، هم با correlated predictors بهتر از LASSO رفتار می‌کند.**

### **چرا Elastic Net برای پروژه شما بهتر از LASSO تنهاست؟**

چون featureهای شما احتمالاً گروهی هستند.

مثلاً در eye-tracking:

gaze_position_x_mean

gaze_position_x_std

gaze_position_y_min

gaze_position_y_max

gaze_path_displacement

fixation_dispersion

این‌ها مستقل کامل نیستند. همه به نوعی نشان می‌دهند کودک کجا نگاه کرده، چقدر gaze حرکت کرده، یا نگاه چقدر پراکنده بوده است.

LASSO ممکن است فقط یکی را نگه دارد و بگوید فقط همین مهم است.

Elastic Net احتمالاً رفتار نرم‌تری دارد و ممکن است چند feature از یک خانواده را با coefficientهای کوچک‌تر نگه دارد یا انتخاب پایدارتری بدهد.

برای همین رئیس‌تان گفت Elastic Net برای داده شما منطقی‌تر است.

### **یک مثال شهودی از پروژه شما**

فرض کنید می‌خواهید در block زیر مدل بسازید:

Outcome: PedsQL_total

Block: Eye × Numeracy

Covariates: age + sex + ADHD severity

Indicators:

- gaze_path_displacement
- fixation_entropy
- saccade_direction_std
- gaze_position_y_min
- fixation_bbox_aspect_ratio
- range_based_fixation_dispersion

Regression معمولی ممکن است بگوید:

R² خوب است

چند p-value زیر .05 است

اما در sample کوچک، این ممکن است overfit باشد.

Stepwise ممکن است بگوید:

gaze_path_displacement

fixation_bbox_aspect_ratio

saccade_angular_velocity

اما اگر sample کمی عوض شود، ممکن است featureهای دیگری انتخاب کند.

LASSO ممکن است بگوید:

فقط gaze_path_displacement را نگه دار

Elastic Net ممکن است بگوید:

gaze_path_displacement

fixation_bbox_aspect_ratio

gaze_position_y_min

ولی coefficientها را کوچک‌تر و محافظه‌کارانه‌تر کند.

حالا شما bootstrap می‌کنید. اگر Elastic Net در ۵۰۰ bootstrap نشان دهد:

gaze_path_displacement selected in 64%

sign negative in 92%

median beta = -2.5

این خیلی معنی‌دارتر از یک p-value خام است.

یعنی:

«در اکثر resampleها، این feature وارد مدل می‌شود و جهت اثرش تقریباً همیشه منفی است.»

اما اگر feature دیگری این‌طور باشد:

selected in 45%

positive sign 52%

negative sign 48%

حتی اگر زیاد انتخاب شود، تفسیرش ضعیف است، چون direction ثابت نیست.

### **تفاوت مهم: selection با prediction فرق دارد**

Elastic Net و LASSO معمولاً برای prediction ساخته شده‌اند، اما در پروژه شما بیشتر به‌عنوان ابزار **stability-based feature discovery** استفاده می‌شوند.

یعنی هدف این نیست که بگویید:

«ما یک مدل پیش‌بینی قوی ساختیم.»

چون N=103 کم است.

هدف بهتر این است:

«کدام featureها وقتی با covariateهای یکسان و selection پایدار بررسی می‌شوند، بیشتر و با جهت ثابت ظاهر می‌شوند؟»

این با نظر رئیس‌تان هماهنگ است.

### **چرا coefficientها در LASSO/Elastic Net را نباید مثل OLS ساده تفسیر کرد؟**

چون coefficientها penalized هستند، یعنی عمداً shrink شده‌اند. مقدارشان bias دارد. این بد نیست؛ برای prediction و selection مفید است. اما برای گزارش مقاله‌ای بهتر است بعد از انتخاب featureها، آن‌ها را دوباره در یک مدل OLS covariate-adjusted بگذارید و coefficient، CI، p-value و partial R² را از آن مدل گزارش کنید.

یعنی:

مرحله selection:

Elastic Net انتخاب می‌کند کدام featureها candidate هستند.

مرحله estimation:

OLS adjusted model اندازه اثر قابل گزارش را تخمین می‌زند.

مثلاً:

Selection:

Elastic Net selected gaze_path_displacement.

Estimation:

PedsQL_total ~ age + sex + ADHD severity + gaze_path_displacement_z

β = -2.7

95% CI = [-5.1, -0.3]

p = .03

اما همچنان اگر FDR یا bootstrap stability کافی نباشد، نتیجه را confirmatory نمی‌نامید.

### **Hyperparameters یعنی چه؟**

در LASSO فقط معمولاً یک چیز اصلی تنظیم می‌شود:

alpha یا lambda

در scikit-learn اسمش معمولاً alpha است، ولی از نظر آماری همان شدت penalty است.

در Elastic Net دو چیز تنظیم می‌شود:

alpha: شدت penalty

l1_ratio: نسبت LASSO به Ridge

در scikit-learn:

l1_ratio = 1.0  → LASSO

l1_ratio = 0.0  → Ridge

l1_ratio = 0.5  → ترکیبی

اگر l1_ratio بالا باشد، مدل sparseتر می‌شود و featureهای بیشتری صفر می‌شوند.

اگر پایین باشد، مدل بیشتر ridge-like می‌شود و featureهای correlated بیشتری را با shrinkage نگه می‌دارد.

### **چرا باید tuning داخل cross-validation باشد؟**

چون اگر با کل داده بهترین alpha را پیدا کنید، دوباره data leakage ایجاد می‌شود. alpha باید فقط از training fold انتخاب شود. در scikit-learn، ElasticNetCV این کار را انجام می‌دهد، ولی باید آن را داخل pipeline درست بگذارید و مراقب باشید preprocessing بیرون CV انجام نشود.

### **LASSO، Elastic Net و Stepwise چه تفاوتی دارند؟**

| **روش** | **چه کار می‌کند؟** | **مزیت** | **مشکل** |
| --- | --- | --- | --- |
| Stepwise | featureها را یکی‌یکی اضافه/حذف می‌کند | ساده، قابل فهم | بسیار ناپایدار، sample-dependent |
| LASSO | coefficient بعضی featureها را صفر می‌کند | feature selection منظم | در correlated features ناپایدار |
| Ridge | همه coefficientها را کوچک می‌کند | خوب برای correlated features | feature selection واضح ندارد |
| Elastic Net | LASSO + Ridge | مناسب برای featureهای زیاد و correlated | tuning پیچیده‌تر |

برای پروژه شما:

Primary: Elastic Net

Secondary: LASSO

Sensitivity: Stepwise

### **یک مثال خیلی ساده عددی**

فرض کن سه feature داریم:

X1 = gaze_path_displacement

X2 = fixation_dispersion

X3 = voice_loudness

و outcome:

PedsQL_total

در داده واقعی، X1 و X2 correlated هستند، چون هر دو eye movement spread را نشان می‌دهند.

OLS ممکن است بدهد:

X1: -5.0

X2: +3.8

X3: +0.4

این عجیب است، چون X1 و X2 رفتار مشابه دارند ولی جهتشان مخالف شده. احتمالاً collinearity یا noise.

LASSO ممکن است بدهد:

X1: -2.9

X2:  0.0

X3:  0.0

مدل ساده شده است، ولی شاید X2 را فقط چون شبیه X1 است حذف کرده.

Elastic Net ممکن است بدهد:

X1: -1.8

X2: -1.2

X3:  0.0

این از نظر رفتاری معقول‌تر است: دو feature eye-related با جهت مشابه، اما shrink شده.

### **برای interpretation در پروژه شما چه چیزی مهم‌تر است؟**

سه چیز:

اول، آیا feature انتخاب می‌شود؟

selection frequency

دوم، آیا جهت اثر ثابت است؟

sign consistency

سوم، آیا بعد از covariateها هنوز باقی می‌ماند؟

covariate robustness

p-value تنها کافی نیست. مخصوصاً با ۱,۳۰۳ indicator.

### **خروجی خوب از Elastic Net برای شما چه شکلی است؟**

نه فقط این:

selected features:

gaze_path_displacement

fixation_bbox_aspect_ratio

بلکه این:

| **feature** | **block** | **selection frequency** | **sign consistency** | **median β** | **verdict** |
| --- | --- | --- | --- | --- | --- |
| gaze_path_displacement | Eye × Numeracy | 0.64 | 0.92 negative | -2.6 | task-specific exploratory |
| fixation_bbox_aspect_ratio | Eye × Numeracy | 0.31 | 0.70 positive | +1.4 | moderate but weak |
| touch_position_y | Stylus × Literacy | 0.48 | 0.58 mixed | +0.9 | unstable |

این جدول به سؤال رئیس‌تان جواب می‌دهد.

### **مهم‌ترین دام در استفاده از LASSO/Elastic Net**

این است که فکر کنیم چون مدل feature را انتخاب کرده، پس feature «واقعاً مهم» است. نه. انتخاب‌شدن یعنی در این داده و تحت این penalty، feature مفید بوده. برای ارزش علمی باید ببینید:

آیا در bootstrap تکرار می‌شود؟

آیا direction ثابت است؟

آیا در taskهای دیگر هم شبیه است؟

آیا بعد از covariate adjustment باقی می‌ماند؟

آیا از نظر رفتاری قابل تفسیر است؟

آیا FDR یا hierarchical model آن را پشتیبانی می‌کند؟

### **جمع‌بندی برای پروژه شما**

LASSO برای شما یعنی:

«از بین featureهای زیاد، یک subset کوچک انتخاب کن و بقیه را صفر کن.»

Elastic Net برای شما یعنی:

«از بین featureهای زیاد و correlated، یک subset نسبتاً پایدارتر انتخاب کن، در حالی که coefficientها را shrink می‌کنی و از overfitting کم می‌کنی.»

در پروژه شما Elastic Net مناسب‌تر از LASSO تنهاست، چون digital indicators درون هر modality × task احتمالاً highly correlated هستند.

اما Elastic Net هم نتیجه نهایی نیست. نتیجه قابل دفاع وقتی ساخته می‌شود که Elastic Net را با bootstrap stability، sign consistency، covariate adjustment و cross-task generality ترکیب کنید.

جمله‌ای که باید در ذهن نگه دارید:

**Stepwise می‌پرسد در همین sample چه چیزی خوب fit می‌شود؛ LASSO می‌پرسد کدام featureها باید حذف شوند؛ Elastic Net می‌پرسد در میان featureهای زیاد و correlated، کدام ساختار ساده‌تر و پایدارتر باقی می‌ماند.**