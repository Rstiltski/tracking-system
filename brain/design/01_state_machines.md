# State Machines v1

**Rule:** Do not use scripts to edit code.

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-01

## Overview

This document defines **deterministic state machines** for the core entities in the system. State machines enforce:

- ✅ **Valid transitions** - Only allowed state changes can occur
- ✅ **Preconditions** - Requirements before transition
- ✅ **Side effects** - Actions triggered by transitions
- ✅ **Invariants** - Rules that must hold in each state

## State Machine Entities

1. [Job State Machine](#1-job-state-machine)
2. [Invoice State Machine](#2-invoice-state-machine)
3. [Payment State Machine](#3-payment-state-machine)
4. [Quote State Machine](#4-quote-state-machine)
5. [Message State Machine](#5-message-state-machine)

---

## 1. Job State Machine

### States

| State | Description | Terminal |
|-------|-------------|----------|
| `DRAFT` | Job created, not yet quoted | ❌ |
| `QUOTED` | Quote sent to customer | ❌ |
| `BOOKED` | Customer accepted, job scheduled | ❌ |
| `SCHEDULED` | Date/time/crew assigned | ❌ |
| `IN_PROGRESS` | Crew on site, job active | ❌ |
| `PAUSED` | Job paused temporarily | ❌ |
| `AWAITING_SIGNOFF` | Work done, awaiting customer approval | ❌ |
| `COMPLETED` | Job finished and signed off | ✅ |
| `INVOICED` | Invoice created for job | ✅ |
| `CANCELLED` | Job cancelled | ✅ |

### Transition Table

| From State | To State | Trigger Command | Preconditions | Side Effects |
|------------|----------|----------------|---------------|--------------|
| `DRAFT` | `QUOTED` | `JobQuote` | • Quote price > 0<br>• Materials estimated | • Set `quoted_at` timestamp<br>• Create `ActionQueue` follow-up |
| `QUOTED` | `BOOKED` | `JobBook` | • Quote accepted<br>• Deposit received (optional) | • Set `booked_at` timestamp<br>• Calculate deposit if required |
| `BOOKED` | `SCHEDULED` | `JobSchedule` | • Date/time set<br>• Crew assigned<br>• No conflicts | • Assign crew<br>• Assign vehicle<br>• Send confirmation to customer |
| `SCHEDULED` | `IN_PROGRESS` | `JobStart` | • Job date is today or past<br>• Crew clocked in | • Start time tracking<br>• Send "on my way" option to customer |
| `IN_PROGRESS` | `PAUSED` | `JobPause` | • Job currently active | • Pause time tracking |
| `PAUSED` | `IN_PROGRESS` | `JobResume` | • Job was paused | • Resume time tracking |
| `IN_PROGRESS` | `AWAITING_SIGNOFF` | `JobComplete` | • Photos uploaded<br>• Checklist complete | • Stop time tracking<br>• Request customer sign-off |
| `AWAITING_SIGNOFF` | `COMPLETED` | `JobAddSignOff` | • Customer sign-off received | • Set `completed_at` timestamp<br>• Trigger invoice creation |
| `COMPLETED` | `INVOICED` | `InvoiceCreate` | • Job completed<br>• No existing invoice | • Create invoice<br>• Set `invoice_no` on job |
| `QUOTED` | `CANCELLED` | `JobCancel` | • Not yet started | • Set `cancelled_at` timestamp<br>• Send cancellation notice |
| `BOOKED` | `CANCELLED` | `JobCancel` | • Cancellation reason provided | • Refund deposit if applicable<br>• Send cancellation notice |
| `SCHEDULED` | `CANCELLED` | `JobCancel` | • Cancellation reason provided | • Unassign crew/vehicle<br>• Refund deposit if applicable |
| `CANCELLED` | `DRAFT` | `JobReopen` | • Admin approval | • Clear cancellation data |
| `COMPLETED` | `IN_PROGRESS` | `JobReopen` | • Admin approval<br>• Issue noted | • Clear completion timestamp |

### Invalid Transitions

These transitions are **explicitly forbidden**:

| From | To | Reason |
|------|-----|--------|
| `DRAFT` | `BOOKED` | Must be quoted first |
| `DRAFT` | `IN_PROGRESS` | Cannot start without booking |
| `IN_PROGRESS` | `CANCELLED` | Must pause or complete first |
| `INVOICED` | `DRAFT` | Cannot un-invoice |
| `COMPLETED` | `DRAFT` | Cannot reset to draft |

### State Invariants

Rules that **must hold** in each state:

| State | Invariants |
|-------|-----------|
| `QUOTED` | • `quoted_price` > 0<br>• `quoted_at` timestamp set |
| `BOOKED` | • `booked_at` timestamp set<br>• Customer ID exists |
| `SCHEDULED` | • `job_date` is set<br>• At least one crew member assigned |
| `IN_PROGRESS` | • Active time entry exists<br>• `start_time` is set |
| `COMPLETED` | • `completed_at` timestamp set<br>• Sign-off photo exists |
| `INVOICED` | • `invoice_no` is set<br>• Invoice record exists |
| `CANCELLED` | • `cancelled_at` timestamp set<br>• Cancellation reason recorded |

---

## 2. Invoice State Machine

### States

| State | Description | Terminal |
|-------|-------------|----------|
| `DRAFT` | Invoice created, not sent | ❌ |
| `SENT` | Invoice sent to customer | ❌ |
| `VIEWED` | Customer viewed invoice | ❌ |
| `PARTIALLY_PAID` | Partial payment received | ❌ |
| `PAID` | Fully paid | ✅ |
| `OVERDUE` | Past due date, unpaid | ❌ |
| `VOID` | Invoice voided | ✅ |

### Transition Table

| From State | To State | Trigger Command | Preconditions | Side Effects |
|------------|----------|----------------|---------------|--------------|
| `DRAFT` | `SENT` | `InvoiceSend` | • Total amount > 0<br>• Customer email/phone exists<br>• Line items present | • Set `sent_at` timestamp<br>• Send invoice via email/SMS<br>• Create `ActionQueue` follow-up |
| `SENT` | `VIEWED` | (Portal tracking) | • Customer opened link | • Set `viewed_at` timestamp |
| `SENT` | `PARTIALLY_PAID` | `PaymentRecord` | • Payment amount < total<br>• Payment amount > 0 | • Update `amount_paid`<br>• Calculate `balance_due`<br>• Send receipt |
| `SENT` | `PAID` | `PaymentRecord` | • Payment amount = balance due | • Set `paid_at` timestamp<br>• Send receipt<br>• Remove from overdue queue |
| `PARTIALLY_PAID` | `PAID` | `PaymentRecord` | • New payment covers balance | • Set `paid_at` timestamp<br>• Send final receipt |
| `SENT` | `OVERDUE` | (System cron) | • `due_date` < today<br>• Not paid | • Set `overdue_at` timestamp<br>• Create overdue chase action |
| `OVERDUE` | `PAID` | `PaymentRecord` | • Payment received | • Clear overdue status<br>• Send receipt |
| `DRAFT` | `VOID` | `InvoiceVoid` | • Reason provided<br>• Admin approval | • Set `voided_at` timestamp<br>• Record void reason |
| `SENT` | `VOID` | `InvoiceVoid` | • Reason provided<br>• Admin approval<br>• Not yet paid | • Send void notice to customer<br>• Create credit note if needed |

### Invalid Transitions

| From | To | Reason |
|------|-----|--------|
| `PAID` | `DRAFT` | Cannot un-pay |
| `PAID` | `VOID` | Cannot void paid invoice (use refund) |
| `VOID` | `SENT` | Cannot un-void |
| `PARTIALLY_PAID` | `DRAFT` | Cannot retract sent invoice with payments |

### State Invariants

| State | Invariants |
|-------|-----------|
| `DRAFT` | • `sent_at` is NULL<br>• No payments recorded |
| `SENT` | • `sent_at` timestamp set<br>• `amount_paid` = 0 |
| `VIEWED` | • `viewed_at` timestamp set |
| `PARTIALLY_PAID` | • `amount_paid` > 0<br>• `amount_paid` < `total`<br>• `balance_due` = `total - amount_paid` |
| `PAID` | • `amount_paid` = `total`<br>• `paid_at` timestamp set<br>• `balance_due` = 0 |
| `OVERDUE` | • `due_date` < today<br>• `amount_paid` < `total` |
| `VOID` | • `voided_at` timestamp set<br>• Void reason recorded |

---

## 3. Payment State Machine

### States

| State | Description | Terminal |
|-------|-------------|----------|
| `PENDING` | Payment recorded, not yet cleared | ❌ |
| `CLEARED` | Payment cleared/confirmed | ✅ |
| `FAILED` | Payment failed | ✅ |
| `REFUNDED` | Payment refunded | ✅ |

### Transition Table

| From State | To State | Trigger Command | Preconditions | Side Effects |
|------------|----------|----------------|---------------|--------------|
| `PENDING` | `CLEARED` | (Stripe webhook)<br>or Manual confirm | • Payment confirmed<br>• Funds received | • Apply to invoice<br>• Update invoice state<br>• Send receipt |
| `PENDING` | `FAILED` | (Stripe webhook)<br>or Manual fail | • Payment declined<br>• Insufficient funds | • Notify customer<br>• Create follow-up action |
| `CLEARED` | `REFUNDED` | `PaymentRefund` | • Refund amount ≤ paid amount<br>• Reason provided<br>• Admin approval | • Process refund<br>• Update invoice balance<br>• Send refund receipt |

### Invalid Transitions

| From | To | Reason |
|------|-----|--------|
| `REFUNDED` | `CLEARED` | Cannot un-refund |
| `FAILED` | `CLEARED` | Failed payment cannot become cleared |
| `PENDING` | `REFUNDED` | Cannot refund uncleared payment |

### State Invariants

| State | Invariants |
|-------|-----------|
| `PENDING` | • `payment_method` is set<br>• `amount` > 0 |
| `CLEARED` | • `cleared_at` timestamp set<br>• Applied to invoice |
| `FAILED` | • `failed_at` timestamp set<br>• Failure reason recorded |
| `REFUNDED` | • `refunded_at` timestamp set<br>• Refund reason recorded<br>• Invoice balance adjusted |

---

## 4. Quote State Machine

### States

| State | Description | Terminal |
|-------|-------------|----------|
| `DRAFT` | Quote being prepared | ❌ |
| `SENT` | Quote sent to customer | ❌ |
| `VIEWED` | Customer viewed quote | ❌ |
| `ACCEPTED` | Customer accepted quote | ✅ |
| `REJECTED` | Customer declined quote | ✅ |
| `EXPIRED` | Quote validity period ended | ✅ |

### Transition Table

| From State | To State | Trigger Command | Preconditions | Side Effects |
|------------|----------|----------------|---------------|--------------|
| `DRAFT` | `SENT` | `QuoteSend` | • Total price > 0<br>• Customer contact exists<br>• Validity period set | • Set `sent_at` timestamp<br>• Send quote via email/SMS<br>• Schedule expiry check |
| `SENT` | `VIEWED` | (Portal tracking) | • Customer opened link | • Set `viewed_at` timestamp |
| `SENT` | `ACCEPTED` | `QuoteAccept` | • Customer confirms acceptance | • Set `accepted_at` timestamp<br>• Create job or update job to BOOKED<br>• Request deposit |
| `SENT` | `REJECTED` | `QuoteReject` | • Customer declines<br>• Optional rejection reason | • Set `rejected_at` timestamp<br>• Create follow-up action<br>• Archive quote |
| `SENT` | `EXPIRED` | (System cron) | • `valid_until` < today<br>• Not accepted | • Set `expired_at` timestamp<br>• Create follow-up action |
| `EXPIRED` | `SENT` | `QuoteSend` | • Updated quote<br>• New validity period | • Reset `sent_at` timestamp<br>• Clear `expired_at` |

### Invalid Transitions

| From | To | Reason |
|------|-----|--------|
| `ACCEPTED` | `REJECTED` | Cannot reject after acceptance |
| `ACCEPTED` | `EXPIRED` | Accepted quotes don't expire |
| `REJECTED` | `ACCEPTED` | Cannot accept rejected quote (send new) |

### State Invariants

| State | Invariants |
|-------|-----------|
| `DRAFT` | • `quoted_price` may be 0 (in progress) |
| `SENT` | • `sent_at` timestamp set<br>• `quoted_price` > 0<br>• `valid_until` date set |
| `ACCEPTED` | • `accepted_at` timestamp set<br>• Job is BOOKED or SCHEDULED |
| `REJECTED` | • `rejected_at` timestamp set<br>• Optional rejection reason |
| `EXPIRED` | • `expired_at` timestamp set<br>• `valid_until` < today |

---

## 5. Message State Machine

### States

| State | Description | Terminal |
|-------|-------------|----------|
| `DRAFT` | Message created, not sent | ❌ |
| `SCHEDULED` | Message scheduled for future send | ❌ |
| `SENDING` | Message being sent | ❌ |
| `SENT` | Message sent successfully | ✅ |
| `DELIVERED` | Message delivered to recipient | ✅ |
| `FAILED` | Message send failed | ✅ |
| `CANCELLED` | Scheduled message cancelled | ✅ |

### Transition Table

| From State | To State | Trigger Command | Preconditions | Side Effects |
|------------|----------|----------------|---------------|--------------|
| `DRAFT` | `SENDING` | `MessageSendSMS`<br>or `MessageSendEmail` | • Recipient contact valid<br>• Message body not empty<br>• No duplicate in last 5 min | • Log to `communication_log`<br>• Call Twilio/SendGrid API |
| `DRAFT` | `SCHEDULED` | `MessageSchedule` | • `send_at` timestamp in future<br>• Recipient valid | • Queue for background job<br>• Log scheduled message |
| `SCHEDULED` | `SENDING` | (System cron) | • `send_at` ≤ now<br>• Not cancelled | • Dequeue message<br>• Call messaging API |
| `SENDING` | `SENT` | (API success) | • API returns 200 OK<br>• Message ID received | • Set `sent_at` timestamp<br>• Update status |
| `SENDING` | `DELIVERED` | (Webhook) | • Delivery confirmation received | • Set `delivered_at` timestamp |
| `SENDING` | `FAILED` | (API error) | • API returns error<br>• Invalid recipient<br>• Rate limit hit | • Set `failed_at` timestamp<br>• Log error reason<br>• Create action to retry |
| `SENT` | `DELIVERED` | (Webhook) | • Delivery confirmation received | • Set `delivered_at` timestamp |
| `SCHEDULED` | `CANCELLED` | `MessageCancel` | • Message not yet sent | • Set `cancelled_at` timestamp<br>• Remove from queue |

### Invalid Transitions

| From | To | Reason |
|------|-----|--------|
| `SENT` | `DRAFT` | Cannot un-send message |
| `DELIVERED` | `FAILED` | Delivered message cannot fail |
| `FAILED` | `SENT` | Failed send cannot become sent (retry creates new message) |
| `CANCELLED` | `SENDING` | Cancelled message cannot be sent |

### State Invariants

| State | Invariants |
|-------|-----------|
| `DRAFT` | • `sent_at` is NULL<br>• `recipient` is set |
| `SCHEDULED` | • `send_at` timestamp in future<br>• Queued for sending |
| `SENDING` | • API call in progress |
| `SENT` | • `sent_at` timestamp set<br>• Message ID recorded |
| `DELIVERED` | • `delivered_at` timestamp set<br>• Delivery confirmation received |
| `FAILED` | • `failed_at` timestamp set<br>• Error reason recorded |
| `CANCELLED` | • `cancelled_at` timestamp set |

---

## State Machine Enforcement

### Brain Implementation

```python
class StateMachine:
    """Base state machine enforcer"""

    def validate_transition(
        self,
        entity_type: str,
        current_state: str,
        target_state: str,
        context: dict
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if transition is allowed.

        Returns:
            (is_valid, error_message)
        """
        # Get transition rules
        transition = self.get_transition(entity_type, current_state, target_state)

        if not transition:
            return False, f"Invalid transition: {current_state} → {target_state}"

        # Check preconditions
        for precondition in transition.preconditions:
            if not precondition.check(context):
                return False, f"Precondition failed: {precondition.description}"

        return True, None

    def execute_side_effects(
        self,
        entity_type: str,
        transition: str,
        context: dict
    ) -> None:
        """Execute side effects after successful transition"""
        side_effects = self.get_side_effects(entity_type, transition)

        for effect in side_effects:
            effect.execute(context)
```

### Error Codes

| Error Code | Description |
|------------|-------------|
| `STATE_INVALID_TRANSITION` | Transition not allowed from current state |
| `STATE_PRECONDITION_FAILED` | Precondition not met |
| `STATE_INVARIANT_VIOLATED` | State invariant would be broken |
| `STATE_TERMINAL_REACHED` | Cannot transition from terminal state |

---

## Testing Requirements

For each state machine:

1. **Transition Tests** - Test all valid transitions
2. **Invalid Transition Tests** - Ensure forbidden transitions fail
3. **Precondition Tests** - Verify preconditions block transitions
4. **Invariant Tests** - Confirm invariants hold after each transition
5. **Side Effect Tests** - Verify side effects execute correctly

---

## Next Steps

1. ✅ Define state machines
2. ⏳ Implement state machine engine (Phase 2)
3. ⏳ Add precondition validators
4. ⏳ Add side effect handlers
5. ⏳ Write comprehensive tests

---

**Status:** ✅ Approved - State machines implemented and tested
**Reviewer:** Development Team
**Approved:** ✅ 2026-01-06 (Job, Invoice, Payment state machines operational)
