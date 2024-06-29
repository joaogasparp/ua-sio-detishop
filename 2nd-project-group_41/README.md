## Overview

This project aims to enhance the security of the first project by implementing the Application Security Verification Standard (ASVS) Level 1 requirements. The ASVS checklist from OWASP was used for the security audit, and identified issues were addressed to ensure a secure and functional online shop.

## Project Structure

### 1. Original Application (`app_org`)

This folder contains the original version of the DETI Memorabilia Online Shop, including instructions on how to run it.

### 2. Improved Secure Application (`app_sec`)

In this folder, you will find the improved and secure version of the online shop, incorporating fixes for the identified security issues. Instructions on how to run the improved application are also provided.

### 3. Analysis (`analysis`)

The analysis folder contains:

- **[Audit Checklist](./análise/ASVS-checklist-en.xlxs):** ASVS Level 1 audit checklist, textual descriptions, logs, and screen captures documenting the identified security issues.

- **[Analysis](./análise/analysis.pdf):** Details on how the identified issues were addressed and the security features implemented.

## Project Description

### Security Enhancements

The following security features have been implemented:

1. **Multi-Factor Authentication (MFA):**
    - Implemented auth0 as the sole authentication method, which offers various options for MFA.

2. **Encrypted Database Storage:**
    - Critical data is encrypted on the web application.

## Authors

- [Guilherme Santos](https://github.com/sonic28g), 107961
- [João Gaspar](https://github.com/joaogasparp), 107708
- [Miguel Ferreira](https://github.com/mgLTF), 93419
- [Pedro Coutinho](https://github.com/pmacoutinho), 93278

## References

- [OWASP ASVS Checklist for Audits](https://github.com/shenril/owasp-asvs-checklist)
- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Proactive Controls](https://owasp.org/www-project-proactive-controls/#div-numbering)
