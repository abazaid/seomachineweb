# Zero Vape SEO Platform - Product & Execution Plan

## 1) الهدف من المنصة
نحن نبني منصة داخلية (لوحة تشغيل) لإدارة SEO بشكل عملي من جمع البيانات إلى تنفيذ المهام عبر:
- Google Analytics 4 (GA4)
- Google Search Console (GSC)
- DataForSEO

المنصة مخصصة لفريق `Zero Vape` لتحويل البيانات إلى قرارات قابلة للتنفيذ بشكل يومي.

---

## 2) الفكرة العامة للنظام
الفكرة الأساسية هي توفير نظام تشغيلي بدل العمل اليدوي المتفرق. يشمل ذلك:
- جمع المؤشرات من عدة مصادر
- تحليل الأداء وتوليد تقارير
- تحويل التوصيات إلى مهام داخل Dashboard موحدة
- إنشاء خط إنتاج محتوى واضح (Research -> Write -> Optimize -> Publish)
- تتبع الحالة التنفيذية والتقدم بشكل مستمر

---

## 3) النطاق (Scope)

### داخل النطاق (In Scope)
- تطبيق ويب كامل (Frontend + Backend)
- نظام مستخدمين وصلاحيات
- ربط المصادر الخارجية عبر APIs
- اختبار الاتصال قبل التشغيل
- توليد تقارير أداء تلقائية
- استخراج توصيات قابلة للتنفيذ
- بناء سير عمل للمحتوى (Pipeline)
- تصدير/نشر المحتوى (حسب التكامل المتاح)
- نشر على VPS عبر Coolify

### خارج النطاق الآن (Out of Scope - v1)
- تعدد الشركات الكامل (Multi-tenant عميق)
- Billing/Subscriptions
- Workflow approvals معقد متعدد المراحل
- لوحات BI متقدمة جدًا (نماذج ML كبيرة)

---

## 4) أدوار المستخدمين
- **Admin**: إدارة الإعدادات العامة والمفاتيح الحساسة
- **SEO Manager**: إدارة التقارير والأولويات وخطة التنفيذ
- **Content Writer/Editor**: إنتاج وتحسين المحتوى

---

## 5) المكونات التقنية

### Backend
- FastAPI
- Celery + Redis (لتنفيذ jobs غير المتزامنة)
- PostgreSQL (تخزين الإعدادات، المستخدمين، التقارير، المهام)
- SQLAlchemy + Alembic

### Frontend
- Next.js (App Router)
- Tailwind + UI components
- واجهة تدعم RTL

### Infra
- Docker / Docker Compose
- Coolify deployment
- Volumes لحفظ البيانات
- Secrets عبر Coolify Environment Variables

---

## 6) هيكل المشروع المقترح

```text
seomachine-web-platform/
  backend/
    app/
      api/
      core/
      services/
      models/
      workers/
      schemas/
    tests/
    alembic/
    requirements.txt
    Dockerfile
  frontend/
    app/
    components/
    lib/
    public/
    Dockerfile
  data_sources/
    modules/                 # Connectors لكل مصدر بيانات
  context/                   # ملفات سياق مشروع Zero Vape
  docker-compose.yml
  .env.example
  README.md
```

---

## 7) خطة التنفيذ المرحلية (Phases)

## Phase 0 - Foundation & Setup
**المدة:** 1-2 أسبوع

### الهدف
تجهيز البيئة الأساسية للتطوير (Backend/Frontend/DB/Queue) بشكل قابل للتشغيل المحلي.

### Deliverables
- Scaffold backend (FastAPI)
- Scaffold frontend (Next.js RTL)
- docker-compose أساسي (postgres + redis + backend + frontend + worker)
- Health endpoints (`/health`)
- صفحة Frontend أولية

### Success Criteria
- `docker compose up` يعمل بدون أخطاء
- كل الخدمات في حالة تشغيل
- backend health = OK

---

## Phase 1 - Auth & Settings Management
**المدة:** 2-3 أسابيع

### الهدف
بناء طبقة المستخدمين والصلاحيات والإعدادات الحساسة لكل مصادر البيانات.

### Deliverables
- Login (email/password) + JWT session
- Roles (admin, manager, writer)
- صفحة Settings تشمل:
  - GA4 property id
  - GSC site url
  - DataForSEO login/password
  - AI provider keys
- تخزين secrets بشكل آمن (DB encrypted أو vault-like + env fallback)

### Success Criteria
- Admin يقدر يضيف/يعدل إعدادات الربط من الواجهة
- المستخدم غير Admin لا يستطيع تعديل الإعدادات الحساسة

---

## Phase 2 - Data Connectors & Connection Tests
**المدة:** 2-4 أسابيع

### الهدف
بناء modules لكل مصدر مع backend API لاختبار صحة الربط قبل التشغيل.

### Deliverables
- Service wrappers لـ GA4/GSC/DataForSEO
- Endpoint: `POST /connections/test`
- واجهة UI تعرض status لكل مصدر (Connected / Failed + سبب)

### Success Criteria
- كل مصدر يقدم نتيجة اختبار واضحة
- رسائل أخطاء مفهومة (missing permission, bad property id, api disabled)

---

## Phase 3 - Performance Review Engine
**المدة:** 3-5 أسابيع

### الهدف
تشغيل تقرير أداء شامل يتم توليده بشكل غير متزامن.

### Deliverables
- Job endpoint: `POST /reports/performance-review`
- Queue execution (Celery)
- حفظ نتائج التقرير في DB + نسخة markdown
- شاشة Reports list + report details

### Success Criteria
- التقرير يعمل بدون timeout على request مباشر
- المستخدم يرى progress (queued/running/done)
- النتائج تظهر كملخص واضح قابل للتنفيذ

---

## Phase 4 - Recommendations to Tasks (Execution Layer)
**المدة:** 3-5 أسابيع

### الهدف
تحويل التوصيات إلى خطة تنفيذ عملية على شكل مهام.

### Deliverables
- تحويل recommendations إلى Task objects
- Task board (To Do / In Progress / Done)
- ربط كل Task مع keyword/page/opportunity source
- Priority scoring لتحديد الأولويات

### Success Criteria
- SEO manager يقدر يستخرج top 5 tasks مباشرة
- المهام مرتبطة بأسباب واضحة قابلة للقياس

---

## Phase 5 - Content Pipeline (Research -> Write -> Optimize)
**المدة:** 4-7 أسابيع

### الهدف
بناء workflow محتوى متكامل من الفكرة حتى النسخة النهائية.

### Deliverables
- إنشاء Research brief لكل keyword
- إنشاء Draft article (AI provider abstraction)
- Optimize pass + checklist
- حفظ الإصدارات (versioning)

### Success Criteria
- كل مرحلة تمر عبر pipeline بدون تدخل يدوي مكرر
- يوجد trace واضح لكل خطوة (inputs/outputs)

---

## Phase 6 - Publishing & Integrations
**المدة:** 2-4 أسابيع

### الهدف
النشر/التصدير إلى القنوات المطلوبة.

### Deliverables
- WordPress publish endpoint (اختياري v1.5)
- Export markdown/csv/pdf
- Audit log لكل عملية نشر

### Success Criteria
- Publish/Export يتم بدون أعطال
- يوجد سجل كامل لأي إجراء تم

---

## Phase 7 - Production Hardening & Coolify
**المدة:** 2-3 أسابيع

### الهدف
تجهيز التطبيق للعمل بثبات على VPS + Coolify.

### Deliverables
- Dockerfiles production-ready
- docker-compose إنتاجي
- Coolify env templates
- backups strategy (DB + volumes)
- monitoring basics (logs + uptime checks)

### Success Criteria
- deployment ناجح على Coolify
- restart-safe + البيانات محفوظة
- health checks مستقرة

---

## 8) خطوات النشر عبر Coolify (مختصر)
1. ارفع المشروع إلى Git (بعد التأكد أن ملفات الأسرار غير مضافة).
2. في Coolify أنشئ Application جديد بنمط `Docker Compose`.
3. اختر الملف: `docker-compose.prod.yml`.
4. انسخ القيم من `.env.coolify.example` إلى Environment Variables في Coolify.
5. اضبط الدومينات:
   - `seo.yourdomain.com` للواجهة الأمامية
   - `seo-api.yourdomain.com` للواجهة الخلفية
6. تأكد أن `BACKEND_CORS_ORIGINS` يحتوي دومين الواجهة (مثال: `https://seo.yourdomain.com`).
7. أضف ملفات Google credentials كـ Secrets/Files في Coolify وحدد مساراتها في:
   - `GA4_CREDENTIALS_PATH`
   - `GSC_CREDENTIALS_PATH`
8. نفذ Deploy ثم اختبر:
   - `GET /health`
   - تسجيل الدخول
   - اختبار الاتصالات (`POST /api/v1/connections/test`)

---

## 9) متغيرات البيئة الأساسية (Production)
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `GA4_PROPERTY_ID`
- `GA4_CREDENTIALS_JSON` (أو mounted file)
- `GSC_SITE_URL` (مثال: `sc-domain:zerovape.store`)
- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`
- `AI_PROVIDER` + API KEYs

---

## 10) Definition of Done لكل Phase
- الكود + الاختبارات الأساسية
- توثيق واضح في README أو docs
- Endpoint/API contract واضح
- Demo قابل للتنفيذ محليًا
- No regressions في الميزات السابقة

---

## 11) المخاطر المتوقعة
- إعدادات Google APIs غير صحيحة أو غير مفعلة
- API rate limits مع المصادر الخارجية
- تكلفة AI مع زيادة الطلب بدون caching
- طول تنفيذ التقارير يتطلب queue واضحة في UX

### Mitigation
- Connection test + error hints واضحة
- Queue + retries + backoff
- Caching للطلبات المتكررة
- Budget guardrails لطلبات AI

---

## 12) أولويات التنفيذ المقترحة
1. إنهاء Phase 0 كامل
2. Phase 1 (Auth + Settings)
3. Phase 2 (Connection Tests)
4. Phase 3 (Performance Review Live)

**الحد الأدنى القابل للإطلاق (MVP):**
- Login
- Settings
- Test Connections
- Run Performance Review
- View Report + Recommendations

---

## 13) ملاحظات تنظيمية
- استخدم اسم مشروع واضح مثل `seomachine` داخل المستودع.
- لا تخلط كود الإنتاج مع سكربتات تجريبية.
- modules الخارجية تكون معزولة لتسهيل الاختبار والصيانة لاحقًا.

---

## 14) ما تم تنفيذه حتى الآن (مرجعي)

تم تنفيذ **Phase 0 -> Phase 7** بشكل أساسي ويشمل:

- Backend (FastAPI + SQLAlchemy + Celery + Redis broker support)
- Frontend (Next.js RTL)
- Authentication + Roles (admin / manager / writer)
- Settings management (Admin only) مع حفظ مفاتيح المصادر
- Connection tests endpoint + UI status
- Performance review job عبر queue + حفظ النتائج في DB + نسخة Markdown
- Recommendations -> Tasks board مع حالات `todo / in_progress / done`
- Content pipeline: `Research -> Draft -> Optimize` + versioning
- Publishing/Export (markdown/csv) + Audit logs
- ملفات إنتاج أساسية: `docker-compose.prod.yml` + health checks + restart policy

### بيانات دخول افتراضية (Local)
- Email: `admin@zerovape.com`
- Password: `Admin@12345`

### المسارات المتاحة (Backend)
- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/settings` (admin)
- `PUT /api/v1/settings` (admin)
- `POST /api/v1/connections/test`
- `POST /api/v1/reports/performance-review`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{id}`
- `POST /api/v1/tasks/from-report/{report_id}`
- `GET /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}/status`
- `POST /api/v1/content/brief`
- `POST /api/v1/content/{content_id}/draft`
- `POST /api/v1/content/{content_id}/optimize`
- `GET /api/v1/content`
- `GET /api/v1/content/{content_id}/versions`
- `POST /api/v1/publishing/export/report/{report_id}?format=markdown|csv`
- `POST /api/v1/publishing/publish/content/{content_id}`
- `GET /api/v1/publishing/audit-logs`

---

## 15) أوامر التشغيل المحلية

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Worker
```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 16) الاختبارات

```bash
PYTHONPATH=backend pytest backend/tests -q
```

تشمل الاختبارات:
- Health (Phase 0)
- Auth + Roles + Settings permissions (Phase 1)
- Connection tests (Phase 2)
- Reports workflow (Phase 3)
- Tasks execution layer (Phase 4)
- Content pipeline + publishing/audit (Phase 5 + 6)
- ملفات الإنتاج/healthchecks الأساسية ضمن تغطية Phase 7
