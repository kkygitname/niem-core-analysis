# NIEM Core 6.0 XSD Analysis
This repository analyzes `niem-core.xsd`, the NIEM Core schema. The goal is to make the schema easier to inspect through summary tables, graph edges, and visualizations.
## Schema metadata
- Target namespace: `https://docs.oasis-open.org/niemopen/ns/model/niem-core/6.0/`
- Version: `ps02`
- Imports: **4**
- Local terms: **31**

## Parsed component counts
- complexTypes: **250**
- simpleTypes: **41**
- elements: **1860**
- abstractElements: **444**
- nillableElements: **1416**
- substitutionGroupElements: **310**
- totalEdges: **3433**

## Relation counts
- extends: **250**
- hasElement: **1416**
- typedBy: **1416**
- substitutionGroup: **310**
- restrictsOrLists: **41**

## Top complex types by number of child elements
| Rank | Complex type | Base type | Child elements | Description |
|---:|---|---|---:|---|
| 1 | `PersonType` | `ObjectType` | 84 | A data type for a human being. |
| 2 | `DocumentType` | `ObjectType` | 65 | A data type for a paper or electronic document. |
| 3 | `ItemType` | `ObjectType` | 46 | A data type for an article or thing. |
| 4 | `OrganizationType` | `ObjectType` | 39 | A data type for a body of people organized for a particular purpose. |
| 5 | `IdentificationType` | `ObjectType` | 29 | A data type for a representation of an identity. |
| 6 | `ActivityType` | `ObjectType` | 28 | A data type for a single or set of related actions, events, or process steps. |
| 7 | `MetadataType` | `ObjectType` | 28 | A data type for information that further qualifies primary data; data about data. |
| 8 | `EmploymentAssociationType` | `AssociationType` | 26 | A data type for an association between an employee and an employer. |
| 9 | `MilitarySummaryType` | `ObjectType` | 20 | A data type for a service of a person in a military. |
| 10 | `FacilityType` | `ObjectType` | 19 | A data type for one or more buildings, places, or structures that together provide a particular service. |
| 11 | `PlanType` | `ObjectType` | 19 | A data type for a detailed proposal for doing or achieving something. |
| 12 | `LocaleType` | `ObjectType` | 18 | A data type for a geopolitical area. |
| 13 | `LocationType` | `ObjectType` | 18 | A data type for geospatial location. |
| 14 | `VehicleType` | `ConveyanceType` | 18 | A data type for a conveyance designed to carry an operator, passengers and/or cargo, over land. |
| 15 | `ObligationType` | `ObjectType` | 17 | A data type for something that is owed to an entity. |

## Top code/simple types by enumeration count
| Rank | Simple type | Base | Enumerations | Description |
|---:|---|---|---:|---|
| 1 | `DirectionCodeSimpleType` | `string` | 16 | A data type for compass directions. |
| 2 | `MilitaryDischargeCategoryCodeSimpleType` | `token` | 9 | A data type for kinds of discharges a person may receive from military service. |
| 3 | `BinaryHashFunctionCodeSimpleType` | `token` | 8 | A data type for a hash function used to generate a hash value representing an object encoded in a binary format. |
| 4 | `DayOfWeekCodeSimpleType` | `token` | 7 | A data type for days of the week. |
| 5 | `PersonUnionStatusCodeSimpleType` | `token` | 7 | A data type describing the legal status of a person's union with another person. |
| 6 | `ContactInformationAvailabilityCodeSimpleType` | `token` | 6 | A data type for a period of time or a situation in which an entity is available to be contacted with the given contact information. |
| 7 | `EmptyReasonCodeSimpleType` | `token` | 6 | A data type for a reason why a data value was not provided. |
| 8 | `PaymentMethodCodeSimpleType` | `token` | 6 | A data type for a specific method of payment. |
| 9 | `PersonPronounsCodeSimpleType` | `token` | 6 | A data type for a set of third-person pronouns that can be used in place of a person's name. |
| 10 | `AddressCategoryCodeSimpleType` | `token` | 5 | A data type for a kind of address. |
| 11 | `FinancialAccountNumberCategoryCodeSimpleType` | `token` | 5 | A data type for a kind of financial account number. |
| 12 | `PersonUnionCategoryCodeSimpleType` | `token` | 5 | A data type describing the legally recognized union between two persons. |
| 13 | `PersonNameCategoryCodeSimpleType` | `token` | 4 | A data type for a kind of person name. |
| 14 | `EmploymentPositionBasisCodeSimpleType` | `token` | 3 | A data type for a nature or duration of the employment position. |
| 15 | `FinancialAccountHolderCodeSimpleType` | `token` | 3 | A data type for a kind of financial account holder. |

## Repository contents
- `data/`: parsed CSV/JSON tables.
- `visualizations/`: PNG/SVG/HTML visualizations.
- `src/analyze_niem.py`: parser and visualization script.
- `docs/analysis.md`: this analysis report.

## How to reproduce
```bash
pip install -r requirements.txt
python src/analyze_niem.py
```
