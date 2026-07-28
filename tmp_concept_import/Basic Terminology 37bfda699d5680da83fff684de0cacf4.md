# Basic Terminology

Category: Foundations (Statistics and Math)

| کلمه | معنی ساده | مثال در پروژه تو |
| --- | --- | --- |
| **Variable / متغیر** | هر چیزی که برای هر کودک اندازه گرفته‌ای و ممکن است بین افراد فرق کند | `age`, `sex`, `PedsQL_total`, eye tracking features |
| **Outcome / Dependent Variable / DV** | چیزی که می‌خواهی توضیح بدهی یا پیش‌بینی کنی | `PedsQL_total` یا `100 - PedsQL_total` |
| **Predictor / Independent Variable / IV** | چیزی که فکر می‌کنی ممکن است outcome را توضیح دهد | eye tracking, voice, keyboard, stylus features |
| **Covariate** | متغیری که جزو سوال اصلی نیست، ولی باید در نظر گرفته شود چون ممکن است روی outcome یا رابطه اصلی اثر بگذارد | سن، جنس، SES، تحصیلات والد، respondent |
| **Covariate adjustment** | یعنی موقع بررسی رابطه‌ی featureهای دیجیتال با PedsQL، اثر سن/جنس/خانواده را هم کنترل کنی | `PedsQL ~ digital features + age + sex + SES` |
| **Confounder / مخدوش‌کننده** | متغیری که هم با predictor مرتبط است، هم با outcome، و اگر کنترل نشود رابطه را اشتباه نشان می‌دهد | اگر SES هم روی استفاده از ابزار دیجیتال اثر بگذارد، هم روی PedsQL، می‌تواند confounder باشد |
| **Confounding** | وقتی یک رابطه ظاهری می‌بینی، ولی بخشی از آن به خاطر یک عامل سوم است | فکر می‌کنی keyboard feature با PedsQL مرتبط است، ولی در واقع بچه‌های بزرگ‌تر هم بهتر تایپ می‌کنند هم PedsQL متفاوتی دارند |
| **Covariance** | یعنی دو چیز با هم بالا و پایین می‌روند | هرچه `ARS_T` بالاتر می‌رود، `PedsQL_total` پایین‌تر می‌آید؛ این یعنی نوعی co-variation/covariance منفی |
| **Correlation** | نسخه استانداردشده و قابل‌فهم‌تر covariance است؛ بین -1 و +1 | correlation بین PSI و PedsQL مثلا منفی است |
| **Association** | رابطه آماری، بدون ادعای علت و معلول | ADHD symptoms با PedsQL association دارد |
| **Effect** | گاهی به معنی اثر آماری استفاده می‌شود، ولی در observational data نباید راحت causal معنی شود | بهتر است بگویی “associated with lower PedsQL”، نه “causes lower PedsQL” |
| **Bias** | خطای سیستماتیک، یعنی نتیجه به یک سمت کج شده | parent-report bias: والد بدبین ممکن است همه چیز را بدتر گزارش کند |
| **Rater effect** | اثر فرد گزارش‌دهنده روی نمره | مادر و پدر ممکن است PedsQL یک کودک را متفاوت نمره بدهند |
| **Reporter bias** | وقتی ویژگی‌های گزارش‌دهنده روی جواب پرسشنامه اثر می‌گذارد | والد مضطرب ممکن است quality of life کودک را پایین‌تر گزارش کند |
| **Residual** | چیزی که بعد از کم کردن بخش قابل‌پیش‌بینی باقی می‌ماند | PedsQL واقعی − PedsQL پیش‌بینی‌شده از age/sex/SES |
| **Residualized outcome** | outcome بعد از حذف اثر covariateها | PedsQLی که اثر سن، جنس، SES، تحصیلات والد از آن کم شده |
| **Adjusted outcome** | شبیه residualized outcome است، ولی دوباره به scale اصلی برگردانده شده | `PedsQL_adjusted = observed - predicted + mean(PedsQL)` |
| **Adjustment** | کنترل کردن اثر متغیرهای مزاحم یا زمینه‌ای | کنترل سن، جنس، SES قبل از بررسی digital features |
| **Mediator / میانجی** | چیزی که در مسیر علت تا معلول قرار دارد | اگر ADHD باعث parenting stress شود و parenting stress باعث PedsQL پایین‌تر شود، PSI mediator است |
| **Moderator / تعدیل‌گر** | چیزی که شدت یا جهت رابطه را تغییر می‌دهد | شاید رابطه‌ی keyboard features با PedsQL در گروه ADHD شدیدتر باشد |
| **Interaction** | مدل آماری moderator | `digital_feature × ADHD_group` |
| **Noise** | بخشی از داده که اطلاعات واقعی مفید ندارد و بیشتر خطا/تصادف است | خطای سنسور، خستگی کودک، بدفهمی والد از پرسشنامه |
| **Signal** | بخش واقعی و قابل‌اتکای اطلاعات | الگویی در eye tracking که واقعا با impairment کودک مرتبط است |
| **Overfitting** | مدل به جای یاد گرفتن الگوی واقعی، جزئیات تصادفی همین sample را حفظ می‌کند | با ۱۰۰۰ feature و ۹۰ کودک، elastic net ممکن است چیزهای تصادفی را انتخاب کند |
| **Stability** | اینکه یک feature در تکرارهای مختلف همچنان انتخاب شود | اگر در bootstrap هر بار featureهای متفاوت انتخاب شوند، stability پایین است |
| **Ceiling effect** | وقتی خیلی‌ها نزدیک سقف نمره‌اند و outcome دیگر تفاوت‌ها را خوب نشان نمی‌دهد | خیلی از بچه‌ها PedsQL نزدیک 100 دارند |
| **Skewness** | کج بودن توزیع داده | PedsQL به سمت نمره‌های بالا جمع شده و سمت پایین دنباله دارد |
| **Transformation** | تغییر شکل outcome یا feature برای مناسب‌تر شدن مدل | `100 - PedsQL` یا `log(100 - PedsQL + 1)` |
| **Impairment score** | تبدیل quality of life به میزان مشکل | `PedsQL_impairment = 100 - PedsQL_total` |

فرق خیلی مهم بین **covariate** و **confounder**:

| مفهوم | فرق شهودی |
| --- | --- |
| **Covariate** | هر متغیر زمینه‌ای که در مدل کنترلش می‌کنی |
| **Confounder** | یک نوع خاص از covariate که اگر کنترل نشود، رابطه اصلی را گمراه‌کننده می‌کند |

مثال خودمونی:

فرض کن می‌خواهی ببینی **keyboard speed** با `PedsQL_impairment` رابطه دارد یا نه.

اما سن کودک هم مهم است:

کودک بزرگ‌تر احتمالا بهتر تایپ می‌کند. کودک بزرگ‌تر شاید PedsQL متفاوتی هم داشته باشد. پس اگر سن را کنترل نکنی، ممکن است فکر کنی keyboard speed با PedsQL رابطه دارد، ولی در واقع سن پشت ماجراست.

اینجا:

| متغیر | نقش |
| --- | --- |
| keyboard speed | predictor اصلی |
| PedsQL impairment | outcome |
| age | confounder احتمالی |
| age داخل مدل | covariate |

پس همه‌ی confounderها covariate هستند، ولی همه‌ی covariateها لزوما confounder نیستند.

یک نقشه ذهنی ساده:

[

Confounder \rightarrow Predictor

]

[

Confounder \rightarrow Outcome

]

یعنی confounder روی هر دو طرف اثر دارد.

مثال:

[

Age \rightarrow Keyboard\ speed

]

[

Age \rightarrow PedsQL

]

پس age می‌تواند رابطه keyboard–PedsQL را قاطی کند.

اما mediator این‌طوری است:

[

ADHD \rightarrow Parenting\ stress \rightarrow PedsQL

]

اینجا اگر PSI را کنترل کنی، ممکن است بخشی از اثر واقعی ADHD را حذف کنی. برای همین گفتیم PSI را بهتر است در sensitivity analysis جداگانه بگذاری.

خلاصه‌ی خیلی کوتاه:

| واژه | ترجمه‌ی ذهنی |
| --- | --- |
| Covariate | چیزی که کنترلش می‌کنم |
| Confounder | چیزی که اگر کنترلش نکنم، رابطه را اشتباه می‌فهمم |
| Covariance | دو چیز با هم بالا/پایین می‌روند |
| Correlation | عدد استاندارد برای شدت این بالا/پایین رفتن |
| Residual | چیزی که بعد از کنترل کردن باقی می‌ماند |
| Adjusted | نتیجه بعد از کنترل کردن |
| Bias | کج‌شدگی سیستماتیک |
| Signal | الگوی واقعی |
| Noise | شلوغی و خطای بی‌فایده |
| Overfitting | مدل زیادی به همین sample می‌چسبد |
| Stability | نتیجه با تکرار عوض نمی‌شود |