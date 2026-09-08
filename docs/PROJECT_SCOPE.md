# Project Scope – Victorian Rental Rights Assistant

## Objective

The Victorian Rental Rights Assistant is a Test-Driven Retrieval-Augmented Generation (RAG) project designed to provide Victorian residential renters with clear, source-grounded information about common rental rights and responsibilities.

The initial prototype uses a manageable knowledge base based on authoritative Victorian rental information so that retrieval performance and answer quality can be systematically evaluated.

## Primary Stakeholder

The primary stakeholders are Victorian residential renters seeking accessible information about their rental rights and responsibilities.

## Jurisdiction

The initial prototype is limited to residential renting in Victoria, Australia.

The knowledge base uses authoritative Consumer Affairs Victoria information and retains source metadata to support traceability and source attribution.

## In-Scope Topics

The initial knowledge base contains seven rental-rights topics:

1. **KB01 – Repairs and Maintenance**
   - Repair responsibilities
   - Urgent and non-urgent repairs

2. **KB02 – Bond Claims and Refunds**
   - Rental bonds
   - Bond claims and refunds
   - Bond disputes

3. **KB03 – Rent Increases**
   - Rent increase notices
   - Frequency and notice requirements
   - Challenging rent increases

4. **KB04 – Property Entry and Inspections**
   - Rental provider entry rights
   - Routine inspections
   - Required notice periods

5. **KB05 – Minimum Rental Standards**
   - Minimum standards for Victorian rental properties
   - Safety and property-condition requirements

6. **KB06 – Moving In and Condition Reports**
   - Moving-in requirements
   - Condition reports
   - Recording the initial condition of the property

7. **KB07 – Ending Rental Agreements and Moving Out**
   - Notice of intention to vacate
   - Ending rental agreements
   - Moving-out requirements

## Out of Scope

The initial prototype does not aim to cover:

- Rental laws outside Victoria
- Commercial leases
- Detailed personalised legal advice or legal representation
- Non-rental property law
- Automated legal decision-making
- Questions that cannot be supported by the available knowledge base

## Expected RAG Behaviour

The RAG system should:

- Retrieve information from the prepared Victorian rental-rights knowledge base.
- Generate answers grounded in retrieved information.
- Maintain traceability to authoritative source material.
- Support source attribution where appropriate.
- Avoid presenting unsupported information as factual.
- Identify questions that fall outside the defined project scope.

## Knowledge Base

The initial knowledge base consists of seven structured documents (`KB01`–`KB07`) stored in the `knowledge_base/` directory.

These documents form the initial corpus for document processing, retrieval experiments and evaluation.
