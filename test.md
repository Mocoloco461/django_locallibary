# תיעוד בדיקות Django

## catalog/tests/test_models.py
- `AuthorModelTest` בודק שמטא-נתונים בסיסיים של מודל המחבר (תוויות, אורך שדות, `__str__`, ו-`get_absolute_url`) עובדים כמתוכנן על אובייקט שנוצר פעם אחת ב-`setUpTestData`.
- `GenreModelTest` מאמת תווית ושורת עזרה של השדה היחיד במודל, וכן תופס `IntegrityError` כדי לוודא שהאילוץ ה-case-insensitive הוגדר בקלאס Meta.
- `BookModelTest` יוצר ספר עם ארבעה ז'אנרים ומוודא שדות טקסט (`title`, `isbn`), קישור ה-URL, והפונקציה `display_genre` שמחזירה שלושה ז'אנרים ראשונים.
- `BookInstanceModelTest` מרכיב עותקי ספר עם `BookLang` ומוודא שהטקסט של `__str__` משקף סטטוס, ושמאפיין `is_overdue` מחזיר אמת/שקר לפי תאריך ההחזרה ביחס להיום.
- `BookLangModelTest` בודק שהמרה למחרוזת משתמשת ב-display value של הבחירה.

## catalog/tests/test_forms.py
- `RenewBookFormTest` מריץ סדרת בדיקות על הטופס `RenewBookForm` (מחלקת Form פשוטה): תווית ושורת עזרה של השדה היחיד, ולאחר מכן תקפות התאריך עבור קלטים בעבר, היום, המקסימום (4 שבועות), וקלט התקף/לא תקף בעתיד הרחוק.

## catalog/tests/test_views.py
- `AuthorListViewTest` משתמש ב-`TemplateDirMixin` כדי לטעון תבנית חלופית ומוודא שה-URL הישיר ו-URL לפי שם מחזירים 200, שהתבנית הספציפית נטענת, שהעמוד הראשון מוגבל ל-10 פריטים ושהעמוד השני מציג את השאר.
- `LoanedBookInstancesByUserListViewTest` מייצר שני משתמשים ו-30 `BookInstance` ומוודא הפניה להתחברות, שימוש בתבנית, סינון הספרים ללווה הנוכחי בלבד, וסידור התוצאות לפי `due_back` במיון עולה (עד 10 פריטים בגלל עימוד).
- `AllLoanedBooksByUserListViewTest` מגדיר קבוצה Librarians ומוודא שהכניסה דורשת התחברות, שמשתמש ללא קבוצה מקבל 403, ושחבר קבוצה יכול לגשת לתצוגה ולקבל רק עותקים בסטטוס `o`.
- `RenewBookInstancesViewTest` בודק את זרימת החידוש: דרישת התחברות, חסימת משתמשים שאין להם חברות ב-Librarians, טעינת התבנית, ערך ראשוני של שלושה שבועות קדימה, עדכון תקין שמפנה ל-`all-borrowed` ומשנה את `due_back`, ושתי בדיקות שגיאה עבור תאריך בעבר ותאריך מעבר לחלון של ארבעה שבועות.
