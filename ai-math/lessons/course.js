// ---------- Course outline ----------
// [lesson id, Persian title, English]. A lesson shows once its file has registered it; until then it is "coming soon".
const COURSE_PLAN = [
  { title: 'جعبه‌ابزار پایه', en: 'Foundations', items: [
    ['function', 'تابع و نمودار', 'Function & Graph'], ['slope', 'شیب خط', 'Slope'], ['derivative', 'مشتق', 'Derivative'],
    ['exponent-log', 'توان و لگاریتم', 'Exponent & Log'], ['chain-rule', 'قاعده‌ی زنجیره‌ای', 'Chain Rule'], ['gradient', 'گرادیان', 'Gradient']] },
  { title: 'آمار', en: 'Statistics', items: [
    ['distribution', 'توزیع چیست؟', 'Distribution'], ['mean', 'میانگین و میانه', 'Mean & Median'], ['variance', 'پراکندگی و چارک‌ها', 'Variance & Quartiles'],
    ['normal', 'توزیع نرمال', 'Normal Distribution'], ['correlation', 'همبستگی', 'Correlation'], ['hypothesis-testing', 'آزمون فرض و p-value', 'Hypothesis Testing'],
    ['anova', 'مقایسه‌ی چند گروه', 'ANOVA']] },
  { title: 'احتمال', en: 'Probability', items: [
    ['probability', 'احتمال', 'Probability'], ['bayes-rule', 'احتمال شرطی و قانون بیز', "Bayes' Rule"], ['maximum-likelihood', 'درست‌نمایی بیشینه', 'Maximum Likelihood']] },
  { title: 'بردارها و ماتریس‌ها', en: 'Vectors & Matrices', items: [
    ['vector', 'بردار چیست؟', 'Vector'], ['vector-add', 'جمع بردارها', 'Vector Addition'], ['vector-scale', 'ضرب عدد در بردار', 'Scalar Multiplication'],
    ['vector-length', 'طول بردار', 'Vector Length'], ['dot-product', 'ضرب داخلی و شباهت', 'Dot Product'], ['matrix', 'ماتریس', 'Matrix'],
    ['matrix-multiplication', 'ضرب ماتریس', 'Matrix Multiplication'], ['eigenvalues', 'مقدار ویژه', 'Eigenvalues']] },
  { title: 'مدل چطور یاد می‌گیرد؟', en: 'How Models Learn', items: [
    ['loss-function', 'تابع خطا', 'Loss Function'], ['gradient-descent', 'گرادیان کاهشی', 'Gradient Descent'], ['overfitting', 'بیش‌برازش', 'Overfitting'],
    ['regularization', 'منظم‌سازی', 'Regularization'], ['bias-variance', 'سوگیری و واریانس', 'Bias–Variance'], ['cross-validation', 'اعتبارسنجی متقابل', 'Cross-Validation'],
    ['metrics', 'معیارهای ارزیابی', 'Accuracy, Precision, Recall'], ['feature-engineering', 'مهندسی ویژگی', 'Feature Engineering']] },
  { title: 'یادگیری ماشین کلاسیک', en: 'Classical ML', items: [
    ['linear-regression', 'رگرسیون خطی', 'Linear Regression'], ['logistic-regression', 'رگرسیون لجستیک', 'Logistic Regression'], ['k-nn', 'نزدیک‌ترین همسایه‌ها', 'k-NN'],
    ['naive-bayes', 'بیز ساده', 'Naive Bayes'], ['decision-tree', 'درخت تصمیم', 'Decision Tree'], ['random-forest-boosting', 'جنگل تصادفی و بوستینگ', 'Random Forest & Boosting'],
    ['k-means', 'خوشه‌بندی', 'K-Means Clustering'], ['pca', 'کاهش بُعد', 'PCA']] },
  { title: 'یادگیری عمیق', en: 'Deep Learning', items: [
    ['neural-network', 'شبکه عصبی', 'Neural Network'], ['backpropagation', 'پس‌انتشار خطا', 'Backpropagation'], ['embedding', 'بردار معنایی', 'Embedding'],
    ['cnn', 'شبکه کانولوشنی', 'CNN'], ['rnn', 'شبکه بازگشتی', 'RNN'], ['attention', 'سازوکار توجه', 'Attention'], ['transformer', 'ترنسفورمر', 'Transformer']] },
  { title: 'مأموریت‌های مصاحبه', en: 'Interview Missions', items: [
    ['m-precision-recall', 'Precision یا Recall؟', 'Precision vs Recall'], ['m-overfitting', 'بیش‌برازش را چطور می‌فهمیم؟', 'How to detect overfitting?'],
    ['m-imbalanced', 'با داده نامتوازن چه کنیم؟', 'Imbalanced Data'], ['m-p-value', 'p-value یعنی چه؟', 'What is a p-value?'],
    ['m-mse-classification', 'چرا MSE برای دسته‌بندی نه؟', 'Why not MSE for classification?'], ['m-l1-sparse', 'چرا L1 وزن‌ها را صفر می‌کند؟', 'Why is L1 sparse?'],
    ['m-bagging-boosting', 'فرق Bagging و Boosting؟', 'Bagging vs Boosting'], ['m-pca', 'PCA دقیقاً چه می‌کند؟', 'What does PCA do?'],
    ['m-vanishing-gradient', 'محو شدن گرادیان چیست؟', 'Vanishing Gradient'], ['m-attention-sqrt-d', 'چرا تقسیم بر √d در توجه؟', 'Why scale attention by √d?']] },
];
const COURSE = COURSE_PLAN.map(c => ({
  title: c.title, en: c.en,
  lessons: c.items.filter(([id]) => LESSONS[id]).map(([id]) => id),
  soon: c.items.filter(([id]) => !LESSONS[id]).map(([, f, e]) => [f, e]),
}));
home();
