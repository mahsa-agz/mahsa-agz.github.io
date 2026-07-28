# Maximum Relevance and Minimum Redundancy Feature Selection Methods

Category: Feature Engineering and Data Preparation
Resource: https://arxiv.org/pdf/1908.05376

**یک feature خوب باید دو شرط داشته باشد:**

1.  **باید Relevant** باشد: یعنی با خروجی `Y` ارتباط زیادی داشته باشد.
2. **نباید redundant** باشد: یعنی با featureهایی که قبلاً انتخاب شده‌اند خیلی شبیه نباشد.

فرمول اصلی PDF این است:

$$
f^{mRMR}(X_i)=I(Y,X_i)-\frac{1}{|S|}\sum_{X_s \in S} I(X_s,X_i)
$$

یعنی: score = relevance - redundancy

- در این فرمول، `Y` خروجی است، مثلاً ADHD/control
- و  `X_i` یک feature کاندید است.
- و `S` مجموعهٔ featureهایی است که قبلاً انتخاب شده‌اند.
- و `I(Y, X_i)` یعنی اطلاعات مشترک بین feature و خروجی. هرچه بزرگ‌تر باشد، feature برای پیش‌بینی مفیدتر است.
- بخش دوم میانگین شباهت feature جدید با featureهای قبلاً انتخاب‌شده است. هرچه بزرگ‌تر باشد، یعنی feature جدید اطلاعات تکراری بیشتری دارد.

برای featureهای عددی، PDF دو نسخهٔ ساده‌تر معرفی می‌کند:

$$
f^{FCD}(X_i)=F(Y,X_i)-\frac{1}{|S|}\sum_{X_s \in S}\rho(X_s,X_i)
$$

$$
f^{FCQ}(X_i)=F(Y,X_i)/\left[\frac{1}{|S|}\sum_{X_s \in S}\rho(X_s,X_i)\right]
$$

اینجا `F(Y, X_i)` یعنی F-statistic؛ یعنی feature چقدر بین کلاس‌ها فرق دارد. `ρ(X_s, X_i)` یعنی correlation بین feature جدید و featureهای قبلاً انتخاب‌شده.

مثال عددی:

فرض کن ۴ feature داریم:

| Feature | F-statistic با ADHD/control |
| --- | --- |
| X1: self-reported inattention | 30 |
| X2: self-reported symptom score | 25 |
| X3: gaze wandering | 20 |
| X4: EEG theta | 5 |

در مرحلهٔ اول هنوز هیچ featureای انتخاب نشده، پس فقط relevance مهم است. چون `X1` بیشترین F-statistic را دارد، اول انتخاب می‌شود.

حالا: S = {X1}

برای انتخاب feature دوم، mRMR هم relevance را نگاه می‌کند، هم correlation با `X1`.

| Candidate | F-statistic | Correlation with X1 | FCQ score |
| --- | --- | --- | --- |
| X2 | 25 | 0.80 | 31.25 |
| X3 | 20 | 0.20 | 100 |
| X4 | 5 | 0.10 | 50 |

محاسبه برای `X2`:

$$
FCQ(X2)=25/0.80=31.25
$$

محاسبه برای `X3`:

$$
FCQ(X3)=20/0.20=100
$$

پس با اینکه `X2` از نظر relevance قوی‌تر از `X3` است، چون خیلی شبیه `X1` است، جریمه می‌شود. mRMR احتمالاً `X3` را انتخاب می‌کند، چون اطلاعات جدیدتری می‌دهد.

بعد از این مرحله:

$$
S = {X1, X3}
$$

برای feature بعدی، redundancy میانگین correlation با هر دو feature انتخاب‌شده است. مثلاً برای `X2`:

$$
redundancy(X2)=\frac{corr(X2,X1)+corr(X2,X3)}{2}
$$

اگر:

$$
corr(X2,X1)=0.80 , corr(X2,X3)=0.30
$$

$$
redundancy(X2)=\frac{0.80+0.30}{2}=0.55
$$

$$
FCQ(X2)=25/0.55=45.45
$$

خلاصه: mRMR از بین ۷۶ feature مقالهٔ ADHD، featureها را یکی‌یکی رتبه‌بندی می‌کند. هر feature وقتی امتیاز خوبی می‌گیرد که هم بین ADHD و کنترل فرق زیادی داشته باشد، هم شبیه featureهای قبلاً انتخاب‌شده نباشد. در آن مقاله، بهترین عملکرد با ۱۱ feature اول به دست آمد و ۶۵ feature دیگر در مدل نهایی حذف شدند.