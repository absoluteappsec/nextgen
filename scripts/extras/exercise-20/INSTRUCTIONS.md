# Exercise 0x20 - Code Review - Cryptographic Analysis

## Objective
Perform a comprehensive analysis of cryptographic controls, identifying any vulnerabilities or flaws in the targeted code base.

## Instructions
### 1. Add Cryptographic Checks

For this exercise, we will be reviewing all encryption protocals and algorithms used within the open source Bridge Troll application.

Add relevant injection checks from the _generic\_checks.md_ list to the template.

```text
## Cryptographic Review
- [ ] What are the standard encryption libraries are used for?
  - [ ] Hashing functions - password hashing, cryptographic signing, etc
  - [ ] Encryption functions - data storage, communications
- [ ] Do the strength of implemented ciphers meet industry standards?
  - [ ] Less than 256-bit encryption
  - [ ] MD5/SHA1 for password hashing
- [ ] Any RC4 stream ciphers
  - [ ] Certificates with less than 1024-bit length keys
  - [ ] All SSL protocol versions
- [ ] Are cryptographic private keys, passwords, and secrets properly protected?
```

Make sure and curate this list to the checks that are valid for the code base being reviewed. Not all checks are appropriate.


### 2. Perform Cryptographic Review
For this exercise, examine the Bridge Troll code base manually and consider the following cryptographic issues.

```text
[ ] Password Encryption
[ ] Session Token Generation
[ ] Outdated Encryption Protocols (e.g. MD5, SHA1)
```

Document all of your findings in _bridge\_troll\_scr.md_.
