# Third-Party Integrations — Backend

## Μέρος Α — Clerk (Authentication)

## Τι είναι το Clerk

Το Clerk είναι ένα **Authentication-as-a-Service** εργαλείο. Αντί να χτίσουμε εμείς το σύστημα login από την αρχή (εγγραφή, sessions, OAuth, 2FA...), το Clerk το κάνει όλο αυτό για εμάς.

Εμείς στο backend χρειαζόμαστε **μόνο να επαληθεύουμε** ότι ο χρήστης είναι πραγματικά αυτός που λέει ότι είναι.

---

## Πώς δουλεύει — Η ροή

```
Frontend                    Backend                   Clerk API
   │                           │                          │
   │── login (email/Google) ──►│                          │
   │◄─ session_token ──────────│◄─ token ─────────────────│
   │                           │                          │
   │── GET /me                 │                          │
   │   Authorization: Bearer   │                          │
   │   <session_token> ───────►│                          │
   │                           │── verify token ─────────►│
   │                           │◄─ user data ─────────────│
   │◄─ { email, name... } ─────│                          │
```

**Βήμα-βήμα:**

1. Ο χρήστης κάνει login μέσω Clerk στο **frontend** (email, Google, GitHub...)
2. Το Clerk δίνει ένα **session token** (JWT) στον browser
3. Κάθε request στέλνει το token στο header: `Authorization: Bearer <token>`
4. Το **backend** στέλνει το token στο Clerk API για επαλήθευση
5. Αν είναι valid → επιστρέφει τα στοιχεία του χρήστη
6. Αν δεν είναι valid → `401 Unauthorized`

---

## Environment Variables

```bash
# .env
CLERK_SECRET_KEY=sk_test_...
```

Το `CLERK_SECRET_KEY` το βρίσκεις στο Clerk Dashboard → API Keys.  
⚠️ Ποτέ δεν το βάζεις hardcoded στον κώδικα και ποτέ δεν το ανεβάζεις στο git.

---

## Dependencies

```bash
pip install fastapi uvicorn httpx python-dotenv
```

---

## Κώδικας

### Setup — `clerk_auth.py`

```python
import os
import httpx
from fastapi import FastAPI, Depends, HTTPException, Header
from dotenv import load_dotenv

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

app = FastAPI(title="Clerk Auth Demo")
```

---

### Dependency: `get_current_user`

Αυτή είναι η καρδιά του Clerk backend. Ένα **dependency** που:

- Διαβάζει το token από το `Authorization` header
- Το στέλνει στο Clerk για επαλήθευση
- Επιστρέφει τα στοιχεία του χρήστη ή πετάει `401`

```python
async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.clerk.com/v1/tokens/verify",
            headers={
                "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                "Content-Type": "application/json",
            },
            params={"token": token},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.json()
```

> **Σημείωση:** Το `Header(...)` σημαίνει ότι το header είναι υποχρεωτικό.  
> Αν δεν υπάρχει, το FastAPI πετάει αυτόματα `422 Unprocessable Entity`.

---

### Public Endpoint — χωρίς auth

```python
@app.get("/")
def root():
    return {"message": "Public endpoint — δεν χρειάζεται login"}
```

---

### Protected Endpoints — με `Depends(get_current_user)`

Για να προστατεύσεις ένα endpoint, απλώς προσθέτεις `Depends(get_current_user)` στα parameters.  
Το FastAPI καλεί αυτόματα τη συνάρτηση πριν τρέξει ο κώδικας του endpoint.

```python
@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "clerk_user_id": current_user.get("sub"),
        "email":         current_user.get("email"),
        "first_name":    current_user.get("first_name"),
    }


@app.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    clerk_user_id = current_user.get("sub")
    return {
        "message": f"Καλωσόρισες! Clerk ID: {clerk_user_id}",
        "data": "Protected data που μόνο logged-in χρήστες βλέπουν",
    }
```

---

## Πώς να το δοκιμάσεις στο Swagger / Postman

Κάθε protected endpoint χρειάζεται το header:

```
Authorization: Bearer <clerk_session_token>
```

Το token το παίρνεις από το Clerk frontend SDK:

```javascript
// Next.js / React με Clerk
const { getToken } = useAuth()
const token = await getToken()

// Μετά το στέλνεις στο API:
fetch("/me", {
  headers: { Authorization: `Bearer ${token}` }
})
```

---

## Σύνοψη

| Έννοια | Εξήγηση |
|--------|---------|
| `session_token` | JWT που δίνει το Clerk στον browser μετά το login |
| `Authorization: Bearer` | Ο τρόπος που στέλνουμε το token σε κάθε request |
| `get_current_user` | Dependency που επαληθεύει το token |
| `Depends(get_current_user)` | Προστατεύει ένα endpoint — αν το token δεν είναι valid, επιστρέφει 401 |
| `sub` | Το Clerk User ID μέσα στο JWT payload |

---
---

# Μέρος Β — Stripe (Payments)

## Τι είναι το Stripe;

Το Stripe είναι ένα **Payments-as-a-Service** εργαλείο. Αντί να χτίσουμε εμείς το σύστημα πληρωμών (κάρτες, ασφάλεια, PCI compliance...), το Stripe το κάνει όλο αυτό για εμάς.

Εμείς στο backend χρειαζόμαστε **μόνο δύο πράγματα:**
1. Να δημιουργούμε **Checkout Sessions** (σελίδα πληρωμής)
2. Να ακούμε **Webhooks** (ειδοποιήσεις από το Stripe)

---

## Πώς δουλεύει — Η ροή

```
Frontend              Backend               Stripe
   │                     │                     │
   │── "Αγορά" ─────────►│                     │
   │                     │── create session ──►│
   │                     │◄─ checkout_url ──────│
   │◄─ checkout_url ─────│                     │
   │                     │                     │
   │── redirect ──────────────────────────────►│
   │        (ο χρήστης πληρώνει στο Stripe)    │
   │                     │                     │
   │                     │◄─ webhook event ─────│
   │                     │  (payment success)   │
   │                     │                     │
   │                     │ [ενεργοποίηση        │
   │                     │  subscription,       │
   │                     │  email, DB update]   │
```

**Βήμα-βήμα:**

1. Ο χρήστης πατάει "Αγορά" στο frontend
2. Το frontend καλεί `POST /create-checkout-session`
3. Το backend δημιουργεί Checkout Session στο Stripe API
4. Το Stripe επιστρέφει ένα **URL** (hosted payment page)
5. Ο χρήστης ανακατευθύνεται εκεί και πληρώνει
6. Το Stripe **χτυπάει** το `POST /webhook` του backend μας
7. Το backend επαληθεύει το event και εκτελεί τη λογική (email, DB κλπ)

> ⚠️ **Σημαντικό:** Η επιβεβαίωση πληρωμής ΔΕΝ γίνεται μέσω του frontend.  
> Το Stripe χτυπάει το backend μας ασύγχρονα. Αυτός είναι ο σωστός τρόπος.

---

## Environment Variables

```bash
# .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

- `STRIPE_SECRET_KEY` → Stripe Dashboard → Developers → API Keys
- `STRIPE_WEBHOOK_SECRET` → Stripe Dashboard → Webhooks → Signing Secret

---

## Dependencies

```bash
pip install fastapi uvicorn stripe python-dotenv
```

---

## Κώδικας

### Setup — `stripe_payments.py`

```python
import os
import stripe
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

app = FastAPI(title="Stripe Payments Demo")
```

---

### Schema

```python
class CheckoutRequest(BaseModel):
    product_name: str
    amount: int       # σε cents — π.χ. 2999 = 29.99€
    currency: str = "eur"
    success_url: str  # π.χ. "https://myapp.com/success"
    cancel_url: str   # π.χ. "https://myapp.com/cancel"
```

> **Γιατί cents;** Το Stripe δουλεύει πάντα με ακέραιους αριθμούς για να αποφεύγει floating point σφάλματα.  
> `2999` = **29,99€** — `1000` = **10,00€**

---

### POST /create-checkout-session

Δημιουργεί τη σελίδα πληρωμής και επιστρέφει το URL.

```python
@app.post("/create-checkout-session")
def create_checkout_session(data: CheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": data.currency,
                        "product_data": {"name": data.product_name},
                        "unit_amount": data.amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=data.success_url,
            cancel_url=data.cancel_url,
        )
        return {"checkout_url": session.url}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Παράδειγμα request:**
```json
POST /create-checkout-session
{
  "product_name": "Premium Plan",
  "amount": 2999,
  "currency": "eur",
  "success_url": "http://localhost:3000/success",
  "cancel_url": "http://localhost:3000/cancel"
}
```

**Παράδειγμα response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

---

### POST /webhook

Το Stripe καλεί αυτό το endpoint αυτόματα μετά από κάθε event.  
Πρέπει **πάντα** να επαληθεύουμε την υπογραφή — αλλιώς οποιοσδήποτε μπορεί να πλαστογραφήσει events.

```python
@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        handle_successful_payment(session)

    elif event_type == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        handle_failed_payment(intent)

    # Πάντα επιστρέφουμε 200 — το Stripe ξαναστέλνει αν δεν λάβει 200
    return {"received": True}
```

---

### Handlers για events

```python
def handle_successful_payment(session: dict):
    amount_total   = session.get("amount_total")
    customer_email = session.get("customer_details", {}).get("email")
    payment_intent = session.get("payment_intent")

    print(f"✅ Πληρωμή επιτυχής!")
    print(f"   Email: {customer_email}")
    print(f"   Ποσό:  {amount_total / 100:.2f}€")
    print(f"   ID:    {payment_intent}")

    # Εδώ μπορείς να:
    # - Ενημερώσεις τη βάση (is_subscribed = True)
    # - Στείλεις email επιβεβαίωσης
    # - Ενεργοποιήσεις features για τον χρήστη


def handle_failed_payment(intent: dict):
    print(f"❌ Πληρωμή απέτυχε: {intent.get('id')}")

    # Εδώ μπορείς να:
    # - Ειδοποιήσεις τον χρήστη
    # - Κάνεις log το σφάλμα
```

---

## Testing με Stripe CLI

Για να δοκιμάσεις τα webhooks **locally** χωρίς να κάνεις deploy:

```bash
# 1. Εγκατάσταση Stripe CLI
# https://stripe.com/docs/stripe-cli

# 2. Login
stripe login

# 3. Forward events στο local server σου
stripe listen --forward-to localhost:8000/webhook

# 4. Σε άλλο terminal, trigger ένα test event
stripe trigger checkout.session.completed
```

> Το Stripe CLI τυπώνει το `STRIPE_WEBHOOK_SECRET` που χρειάζεσαι για το `.env`.

---

## Συχνά Stripe Events

| Event | Πότε |
|-------|------|
| `checkout.session.completed` | Επιτυχής πληρωμή μέσω Checkout |
| `payment_intent.succeeded` | Επιτυχής χρέωση |
| `payment_intent.payment_failed` | Αποτυχημένη χρέωση |
| `customer.subscription.created` | Νέο subscription |
| `customer.subscription.deleted` | Ακύρωση subscription |
| `invoice.payment_failed` | Αποτυχημένη ανανέωση subscription |

---

## Σύνοψη

| Έννοια | Εξήγηση |
|--------|---------|
| `Checkout Session` | Hosted σελίδα πληρωμής που φτιάχνει το Stripe |
| `checkout_url` | Το URL όπου πηγαίνει ο χρήστης για να πληρώσει |
| `webhook` | HTTP request που στέλνει το Stripe στο backend μας για να μας ενημερώσει |
| `stripe_signature` | Υπογραφή που επαληθεύει ότι το webhook έρχεται από το Stripe |
| `amount` σε cents | `2999` = 29,99€ — χωρίς δεκαδικά για αποφυγή σφαλμάτων |
| `mode="payment"` | Εφάπαξ πληρωμή — υπάρχει και `mode="subscription"` |
