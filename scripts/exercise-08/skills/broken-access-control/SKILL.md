---
name: broken-access-control
description: "Use this skill when analyzing Django applications for OWASP 2025 A01: Broken Access Control and Broken Object-Level Authorization (BOLA) vulnerabilities."
license: MIT
metadata:
  author: absoluteappsec
  version: "1.0"
---

# A01:2025 Broken Access Control — Django Analysis Skill

## Overview

Broken Access Control is the #1 vulnerability in the OWASP Top 10 2025. It occurs when users can act outside their intended permissions — viewing other users' data, modifying records they don't own, or escalating privileges.

A critical subset is **Broken Object-Level Authorization (BOLA)**, where API endpoints expose object identifiers and fail to verify the requesting user has access to that specific object.

## Attack Scenarios

### Scenario 1: ID Manipulation (IDOR)
An attacker modifies a URL parameter to access another user's resource:
```
GET /api/messages/67/   →  attacker changes to  →  GET /api/messages/68/
```
If the view fetches by ID without checking ownership, the attacker sees another user's message.

### Scenario 2: Request Body Exploitation
An attacker modifies a JSON payload to change resource ownership:
```json
{"title": "My Report", "user": 42}
```
If the view trusts the `user` field from the request body instead of deriving it from the authenticated session, the attacker can assign resources to any user.

### Scenario 3: Predictable Sequential IDs
Auto-incrementing integer IDs (1, 2, 3...) let attackers enumerate every object in the system. Combined with missing authorization, this turns a single IDOR into a full data breach.

## Vulnerable Patterns to Detect

### Pattern 1: Object Lookup Without Ownership Check
```python
# VULNERABLE: fetches by ID alone, any authenticated user can access any item
def view_item(request, item_id):
    item = Item.objects.get(id=item_id)
    return render(request, "item.html", {"item": item})

# VULNERABLE: delete without ownership verification
def delete_item(request, item_id):
    Item.objects.filter(id=item_id).delete()
    return redirect("/items/")
```

### Pattern 2: Missing Authentication Entirely
```python
# VULNERABLE: no @login_required, no LoginRequiredMixin
def sensitive_view(request):
    return render(request, "admin_dashboard.html")
```

### Pattern 3: Trusting Client-Supplied Ownership
```python
# VULNERABLE: owner comes from POST data, attacker can set any user
def create_report(request):
    Report.objects.create(
        title=request.POST["title"],
        owner_id=request.POST["user_id"],  # should be request.user
    )
```

### Pattern 4: Unfiltered Querysets
```python
# VULNERABLE: returns ALL objects regardless of who is requesting
class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    # no get_queryset override to filter by request.user
```

### Pattern 5: Missing Function-Level Access Control
```python
# VULNERABLE: GET is protected but POST/DELETE on the same resource is not
@login_required
def view_project(request, project_id):
    ...

# No decorator — anyone can delete
def delete_project(request, project_id):
    Project.objects.filter(id=project_id).delete()
```

## Secure Patterns (What Fixes Look Like)

### Fix 1: Use UUIDs Instead of Sequential IDs
```python
import uuid
from django.db import models

class Subscription(models.Model):
    id = models.UUIDField(unique=True, primary_key=True,
                         editable=False, default=uuid.uuid4)
```

### Fix 2: Track Resource Ownership
```python
class Report(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE,
                             related_name="reports")
    title = models.CharField(max_length=250)
```

### Fix 3: Derive Owner from Authentication Token
```python
class ReportView(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)  # owner from session, not request body
            return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### Fix 4: Filter Querysets by Ownership
```python
class ReportView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return Report.objects.filter(owner=self.request.user)
        return Report.objects.all()
```

### Fix 5: Custom Object-Level Permission Class
```python
from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser
```

### Fix 6: Ownership Check in Function-Based Views
```python
@login_required
def delete_item(request, item_id):
    Item.objects.filter(id=item_id, owner=request.user).delete()
    return redirect("/items/")
```

## Analysis Checklist

When reviewing Django code for A01 Broken Access Control:

1. **For every view/endpoint**: Does it have `@login_required`, `LoginRequiredMixin`, or `permissions.IsAuthenticated`? If not, should it?
2. **For every object lookup by ID**: Is the queryset filtered by `request.user` or does a permission class call `has_object_permission`?
3. **For every create/update operation**: Is the owner derived from `request.user` or from client-supplied input?
4. **For every model with a user/owner FK**: Do all views that query it filter by the current user?
5. **For every DELETE endpoint**: Does it verify ownership before deleting?
6. **Check for sequential integer PKs**: Are predictable IDs used on sensitive models?
7. **Check middleware**: Is there global auth middleware, or is auth enforced per-view?
8. **Check URL patterns**: Can admin URLs be reached by guessing paths?

## References

- https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/
- https://www.stackhawk.com/blog/django-broken-object-level-authorization-guide-examples-and-prevention/
- CWE-862: Missing Authorization
- CWE-639: Authorization Bypass Through User-Controlled Key
- CWE-285: Improper Authorization
- CWE-269: Improper Privilege Management
