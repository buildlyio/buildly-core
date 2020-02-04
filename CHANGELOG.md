# Change Log

## [0.6.1](https://github.com/buildlyio/buildly-core/tree/0.6.1) (2020-02-04)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.6.0...0.6.1)

**Implemented enhancements:**

- Implement LDAP User Authentication [\#276](https://github.com/buildlyio/buildly-core/issues/276)

**Fixed bugs:**

- OAuth User endpoint returns forbidden [\#252](https://github.com/buildlyio/buildly-core/issues/252)

**Closed issues:**

- CLI stepwise wizard for creating a buildly core application and service. [\#267](https://github.com/buildlyio/buildly-core/issues/267)
- Services [\#266](https://github.com/buildlyio/buildly-core/issues/266)

**Merged pull requests:**

- \[Security\] Bump django from 2.2.8 to 2.2.9 [\#295](https://github.com/buildlyio/buildly-core/pull/295) ([jefmoura](https://github.com/jefmoura))

## [0.6.0](https://github.com/buildlyio/buildly-core/tree/0.6.0) (2020-02-03)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.5.0...0.6.0)

**Implemented enhancements:**

- Remove old implementation of Buildly Core gateway [\#260](https://github.com/buildlyio/buildly-core/issues/260)
- Remove User, Organization and Groups and Related tables to Core APP [\#214](https://github.com/buildlyio/buildly-core/issues/214)

**Fixed bugs:**

- Sending files with POST requests fail with the async gateway [\#259](https://github.com/buildlyio/buildly-core/issues/259)
- DELETE requests fail with async gateway [\#258](https://github.com/buildlyio/buildly-core/issues/258)

**Closed issues:**

- Remove dependency to ChargeBee [\#273](https://github.com/buildlyio/buildly-core/issues/273)
- Remove GraphQL integration [\#196](https://github.com/buildlyio/buildly-core/issues/196)
- Buildly Core [\#187](https://github.com/buildlyio/buildly-core/issues/187)

**Merged pull requests:**

- Replace oauthuser with coreuser/me endpoint [\#294](https://github.com/buildlyio/buildly-core/pull/294) ([jefmoura](https://github.com/jefmoura))
- Update LDAP configuration and information [\#293](https://github.com/buildlyio/buildly-core/pull/293) ([jefmoura](https://github.com/jefmoura))
- Update landing page structure [\#291](https://github.com/buildlyio/buildly-core/pull/291) ([jefmoura](https://github.com/jefmoura))
- Merge fixes that were done previously [\#290](https://github.com/buildlyio/buildly-core/pull/290) ([jefmoura](https://github.com/jefmoura))
- Remove unneeded dependencies [\#288](https://github.com/buildlyio/buildly-core/pull/288) ([jefmoura](https://github.com/jefmoura))

## [0.5.0](https://github.com/buildlyio/buildly-core/tree/0.5.0) (2019-12-31)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.4.0...0.5.0)

**Closed issues:**

- Core Lean or Scale [\#265](https://github.com/buildlyio/buildly-core/issues/265)
- New app or migrate question and response [\#264](https://github.com/buildlyio/buildly-core/issues/264)

**Merged pull requests:**

- Update landing page [\#275](https://github.com/buildlyio/buildly-core/pull/275) ([jefmoura](https://github.com/jefmoura))
- Remove User, Organization and Groups and Related tables to Core APP [\#274](https://github.com/buildlyio/buildly-core/pull/274) ([jefmoura](https://github.com/jefmoura))
- Fix broken links in the README file [\#272](https://github.com/buildlyio/buildly-core/pull/272) ([jefmoura](https://github.com/jefmoura))
- Update some of the dependencies [\#271](https://github.com/buildlyio/buildly-core/pull/271) ([jefmoura](https://github.com/jefmoura))
- \[Security\] Bump django from 2.2.6 to 2.2.8 [\#268](https://github.com/buildlyio/buildly-core/pull/268) ([dependabot-preview[bot]](https://github.com/apps/dependabot-preview))
- Update changelog with the latest version 0.4.0 [\#263](https://github.com/buildlyio/buildly-core/pull/263) ([jefmoura](https://github.com/jefmoura))

## [0.4.0](https://github.com/buildlyio/buildly-core/tree/0.4.0) (2019-11-08)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.3.0...0.4.0)

**Implemented enhancements:**

- Allow users to specify the swagger.json endpoint for a LogicModule [\#229](https://github.com/buildlyio/buildly-core/issues/229)
- Add user group permission check to service level [\#209](https://github.com/buildlyio/buildly-core/issues/209)

**Fixed bugs:**

- Implement invitation token invalidation [\#199](https://github.com/buildlyio/buildly-core/issues/199)

**Closed issues:**

- Update Django version to 2.2.6 [\#222](https://github.com/buildlyio/buildly-core/issues/222)
- Remove Celery and RabbitMQ integration [\#200](https://github.com/buildlyio/buildly-core/issues/200)

**Merged pull requests:**

- Implementation of LDAP Auth [\#292](https://github.com/buildlyio/buildly-core/pull/292) ([jefmoura](https://github.com/jefmoura))
- Re-organize scripts [\#262](https://github.com/buildlyio/buildly-core/pull/262) ([jefmoura](https://github.com/jefmoura))
- Implement service group permission level [\#250](https://github.com/buildlyio/buildly-core/pull/250) ([jefmoura](https://github.com/jefmoura))
- Remove Celery and RabbitMQ integration [\#249](https://github.com/buildlyio/buildly-core/pull/249) ([jefmoura](https://github.com/jefmoura))
- Bump Django from 2.2.4 to 2.2.6 [\#248](https://github.com/buildlyio/buildly-core/pull/248) ([msradam](https://github.com/msradam))
- Fix test suite failure for IndexViewTest [\#247](https://github.com/buildlyio/buildly-core/pull/247) ([msradam](https://github.com/msradam))
- Add Guidelines section to the docs [\#242](https://github.com/buildlyio/buildly-core/pull/242) ([jefmoura](https://github.com/jefmoura))
- Add release process section documentation to the docs [\#241](https://github.com/buildlyio/buildly-core/pull/241) ([jefmoura](https://github.com/jefmoura))
- Bump django-filter from 2.1.0 to 2.2.0 [\#239](https://github.com/buildlyio/buildly-core/pull/239) ([dependabot-preview[bot]](https://github.com/apps/dependabot-preview))
- Bump pytest-django from 3.5.1 to 3.6.0 [\#237](https://github.com/buildlyio/buildly-core/pull/237) ([dependabot-preview[bot]](https://github.com/apps/dependabot-preview))
- Bump httpretty from 0.9.6 to 0.9.7 [\#236](https://github.com/buildlyio/buildly-core/pull/236) ([dependabot-preview[bot]](https://github.com/apps/dependabot-preview))
- Bump ipdb from 0.11 to 0.12.2 [\#235](https://github.com/buildlyio/buildly-core/pull/235) ([dependabot-preview[bot]](https://github.com/apps/dependabot-preview))
- Added Swagger docs endpoint field to LogicModule [\#234](https://github.com/buildlyio/buildly-core/pull/234) ([msradam](https://github.com/msradam))
- Modified invitation token validation to prevent token reuse [\#233](https://github.com/buildlyio/buildly-core/pull/233) ([msradam](https://github.com/msradam))

## [0.3.0](https://github.com/buildlyio/buildly-core/tree/0.3.0) (2019-10-17)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.2.4...0.3.0)

**Implemented enhancements:**

- Create API endpoints to manage access tokens [\#208](https://github.com/buildlyio/buildly-core/issues/208)
- Create API endpoints to manage Authentication process [\#207](https://github.com/buildlyio/buildly-core/issues/207)
- Update API landing page [\#186](https://github.com/buildlyio/buildly-core/issues/186)

**Fixed bugs:**

- Fix Travis pipeline when PR comes from an external repo [\#221](https://github.com/buildlyio/buildly-core/issues/221)
- OpenAPI doc shows error if an instance of a logic module isn't available [\#198](https://github.com/buildlyio/buildly-core/issues/198)

**Closed issues:**

- Manage all generated refresh tokens [\#232](https://github.com/buildlyio/buildly-core/issues/232)
- Create a tutorial explaining how to deploy Buidlly to Minikube [\#225](https://github.com/buildlyio/buildly-core/issues/225)
- Convert Documentation from Markdown to reStructured [\#224](https://github.com/buildlyio/buildly-core/issues/224)
- Create endpoints to manage services [\#218](https://github.com/buildlyio/buildly-core/issues/218)
- Make password of admin user during creation dynamic [\#211](https://github.com/buildlyio/buildly-core/issues/211)

**Merged pull requests:**

- Add OAuth Application endpoints [\#231](https://github.com/buildlyio/buildly-core/pull/231) ([jefmoura](https://github.com/jefmoura))
- Add access & refresh token endpoints [\#230](https://github.com/buildlyio/buildly-core/pull/230) ([jefmoura](https://github.com/jefmoura))
- New tutorial for Minikube [\#227](https://github.com/buildlyio/buildly-core/pull/227) ([jefmoura](https://github.com/jefmoura))
- Convert documentation files to reStructured [\#226](https://github.com/buildlyio/buildly-core/pull/226) ([jefmoura](https://github.com/jefmoura))
- Dynamic superuser password [\#223](https://github.com/buildlyio/buildly-core/pull/223) ([jefmoura](https://github.com/jefmoura))
- Add sample RSA keys for testing [\#220](https://github.com/buildlyio/buildly-core/pull/220) ([jefmoura](https://github.com/jefmoura))
- Modified Swagger URL retrieval to handle exceptions for unavailable endpoint [\#219](https://github.com/buildlyio/buildly-core/pull/219) ([msradam](https://github.com/msradam))
- Update Travis file to build docker image and push to registry [\#216](https://github.com/buildlyio/buildly-core/pull/216) ([jefmoura](https://github.com/jefmoura))
- Reset migration scripts [\#215](https://github.com/buildlyio/buildly-core/pull/215) ([jefmoura](https://github.com/jefmoura))
- Adjust documentation and templates [\#204](https://github.com/buildlyio/buildly-core/pull/204) ([jefmoura](https://github.com/jefmoura))
- Restructure the documentation with Sphinx [\#203](https://github.com/buildlyio/buildly-core/pull/203) ([jefmoura](https://github.com/jefmoura))
- New landing page [\#193](https://github.com/buildlyio/buildly-core/pull/193) ([glind](https://github.com/glind))
- Add Bandit to CI pipeline to find security issues [\#192](https://github.com/buildlyio/buildly-core/pull/192) ([jefmoura](https://github.com/jefmoura))
- Rename everything to buildly [\#185](https://github.com/buildlyio/buildly-core/pull/185) ([jefmoura](https://github.com/jefmoura))
- Add travis yaml configuration [\#184](https://github.com/buildlyio/buildly-core/pull/184) ([jefmoura](https://github.com/jefmoura))
- Upgrade Django framework to 2.2.4 for security reasons [\#183](https://github.com/buildlyio/buildly-core/pull/183) ([jefmoura](https://github.com/jefmoura))
- Update JWT Generator [\#182](https://github.com/buildlyio/buildly-core/pull/182) ([jefmoura](https://github.com/jefmoura))
- Rewrite README to use the new structure [\#180](https://github.com/buildlyio/buildly-core/pull/180) ([jefmoura](https://github.com/jefmoura))
- Fix ContentTypeError on empty responses with AsyncClient - PLAT-569 [\#179](https://github.com/buildlyio/buildly-core/pull/179) ([ralfzen](https://github.com/ralfzen))
- Add LogicModuleModelManager [\#177](https://github.com/buildlyio/buildly-core/pull/177) ([ralfzen](https://github.com/ralfzen))
- Docs update [\#176](https://github.com/buildlyio/buildly-core/pull/176) ([lemkeb](https://github.com/lemkeb))
- Remove deploy-docs step [\#175](https://github.com/buildlyio/buildly-core/pull/175) ([lemkeb](https://github.com/lemkeb))
- Remove SOCIAL\_AUTH\_CREDENTIALS [\#174](https://github.com/buildlyio/buildly-core/pull/174) ([ralfzen](https://github.com/ralfzen))
- Remove envars.yml [\#173](https://github.com/buildlyio/buildly-core/pull/173) ([ralfzen](https://github.com/ralfzen))
- New GPL v3 license [\#172](https://github.com/buildlyio/buildly-core/pull/172) ([glind](https://github.com/glind))
- remove old license [\#171](https://github.com/buildlyio/buildly-core/pull/171) ([glind](https://github.com/glind))

## [0.2.4](https://github.com/buildlyio/buildly-core/tree/0.2.4) (2019-08-01)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.2.3...0.2.4)

**Merged pull requests:**

- Add WorkflowLevel2Status-model, -viewset and filters - CU-799, CU-800 [\#170](https://github.com/buildlyio/buildly-core/pull/170) ([ralfzen](https://github.com/ralfzen))
- Adapt loadrelationships command - CU-784 [\#169](https://github.com/buildlyio/buildly-core/pull/169) ([ralfzen](https://github.com/ralfzen))
- Improve datamesh [\#168](https://github.com/buildlyio/buildly-core/pull/168) ([ralfzen](https://github.com/ralfzen))
- Extend related\_logic\_modules in DataMesh with origins [\#167](https://github.com/buildlyio/buildly-core/pull/167) ([ralfzen](https://github.com/ralfzen))
- fix drone tests failure [\#166](https://github.com/buildlyio/buildly-core/pull/166) ([docktorrr](https://github.com/docktorrr))
- PLAT-567: endpoints for Data Mesh models [\#165](https://github.com/buildlyio/buildly-core/pull/165) ([docktorrr](https://github.com/docktorrr))
- PLAT-527: local Data Mesh [\#164](https://github.com/buildlyio/buildly-core/pull/164) ([docktorrr](https://github.com/docktorrr))
- Update Drone config + sync docs [\#163](https://github.com/buildlyio/buildly-core/pull/163) ([lemkeb](https://github.com/lemkeb))
- Remove walhall notification from drone [\#162](https://github.com/buildlyio/buildly-core/pull/162) ([docktorrr](https://github.com/docktorrr))

## [0.2.3](https://github.com/buildlyio/buildly-core/tree/0.2.3) (2019-07-21)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.2.2...0.2.3)

**Merged pull requests:**

-  PLAT-557: Gateway refactoring to use DataMesh object [\#161](https://github.com/buildlyio/buildly-core/pull/161) ([docktorrr](https://github.com/docktorrr))
- Change relationship name in data mesh load script [\#160](https://github.com/buildlyio/buildly-core/pull/160) ([ralfzen](https://github.com/ralfzen))
- PLAT-557: allow async extend\_data to call from outer event loop [\#159](https://github.com/buildlyio/buildly-core/pull/159) ([docktorrr](https://github.com/docktorrr))
- Remove obsolete permissions from JoinRecord-View [\#158](https://github.com/buildlyio/buildly-core/pull/158) ([ralfzen](https://github.com/ralfzen))
- PLAT-557: DataMesh service for decoupling from gateway [\#157](https://github.com/buildlyio/buildly-core/pull/157) ([docktorrr](https://github.com/docktorrr))
- PLAT-526: tests for async gateway view [\#156](https://github.com/buildlyio/buildly-core/pull/156) ([docktorrr](https://github.com/docktorrr))
- Enable new gateway in root [\#155](https://github.com/buildlyio/buildly-core/pull/155) ([ralfzen](https://github.com/ralfzen))
- Sync with docs site [\#154](https://github.com/buildlyio/buildly-core/pull/154) ([lemkeb](https://github.com/lemkeb))
- PLAT-526: add tests for the new gateway with datamesh aggregation [\#153](https://github.com/buildlyio/buildly-core/pull/153) ([docktorrr](https://github.com/docktorrr))
- PLAT-561: old data mesh in GatewayRequest [\#152](https://github.com/buildlyio/buildly-core/pull/152) ([docktorrr](https://github.com/docktorrr))
- PLAT-557: remove gateway.LogicModule dependency from datamesh app [\#151](https://github.com/buildlyio/buildly-core/pull/151) ([docktorrr](https://github.com/docktorrr))
- Fix view in the urls [\#150](https://github.com/buildlyio/buildly-core/pull/150) ([docktorrr](https://github.com/docktorrr))
- CU-743 - Add JoinRecord List View [\#149](https://github.com/buildlyio/buildly-core/pull/149) ([ralfzen](https://github.com/ralfzen))
- PLAT-525: tests for updated gateway [\#148](https://github.com/buildlyio/buildly-core/pull/148) ([docktorrr](https://github.com/docktorrr))
- CU-761 Add `id` to serializers [\#147](https://github.com/buildlyio/buildly-core/pull/147) ([katyanna](https://github.com/katyanna))
- PLAT-526: async requests in the gateway [\#146](https://github.com/buildlyio/buildly-core/pull/146) ([docktorrr](https://github.com/docktorrr))
- Reverse data mesh CU-759 [\#145](https://github.com/buildlyio/buildly-core/pull/145) ([ralfzen](https://github.com/ralfzen))
- Set endpoint mandatory in LogicModuleModel [\#144](https://github.com/buildlyio/buildly-core/pull/144) ([ralfzen](https://github.com/ralfzen))
- Add query\_params and fix POST, PUT, PATCH data [\#143](https://github.com/buildlyio/buildly-core/pull/143) ([ralfzen](https://github.com/ralfzen))
- PLAT-554: update gateway exceptions status codes [\#142](https://github.com/buildlyio/buildly-core/pull/142) ([docktorrr](https://github.com/docktorrr))

## [0.2.2](https://github.com/buildlyio/buildly-core/tree/0.2.2) (2019-07-05)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.2.1...0.2.2)

**Merged pull requests:**

- Optimize load relationship command - CU-742 [\#141](https://github.com/buildlyio/buildly-core/pull/141) ([ralfzen](https://github.com/ralfzen))

## [0.2.1](https://github.com/buildlyio/buildly-core/tree/0.2.1) (2019-07-04)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.2.0...0.2.1)

**Merged pull requests:**

- Optimize load data mesh relationship command - CU-742 [\#140](https://github.com/buildlyio/buildly-core/pull/140) ([ralfzen](https://github.com/ralfzen))

## [0.2.0](https://github.com/buildlyio/buildly-core/tree/0.2.0) (2019-07-04)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.1.4...0.2.0)

**Merged pull requests:**

- Switch to python 3.7 [\#139](https://github.com/buildlyio/buildly-core/pull/139) ([docktorrr](https://github.com/docktorrr))
- Add file handling [\#138](https://github.com/buildlyio/buildly-core/pull/138) ([ralfzen](https://github.com/ralfzen))
- Add command for loading contact-siteprofile-relationships CU-742 [\#137](https://github.com/buildlyio/buildly-core/pull/137) ([ralfzen](https://github.com/ralfzen))
- Fix unique\_together constraint on JoinRecord [\#136](https://github.com/buildlyio/buildly-core/pull/136) ([ralfzen](https://github.com/ralfzen))
- PLAT-525: optimizing gateway [\#135](https://github.com/buildlyio/buildly-core/pull/135) ([docktorrr](https://github.com/docktorrr))
- PLAT-542: fix CoreUser & CoreGroup permissions [\#134](https://github.com/buildlyio/buildly-core/pull/134) ([docktorrr](https://github.com/docktorrr))
- PLAT-465: datamesh list aggregation [\#133](https://github.com/buildlyio/buildly-core/pull/133) ([docktorrr](https://github.com/docktorrr))
- DataMesh aggregation improvements [\#132](https://github.com/buildlyio/buildly-core/pull/132) ([docktorrr](https://github.com/docktorrr))
- PLAT-536: restrict to view core groups only from user's organization [\#131](https://github.com/buildlyio/buildly-core/pull/131) ([docktorrr](https://github.com/docktorrr))
- Add DataMesh join with DataMesh-models [\#130](https://github.com/buildlyio/buildly-core/pull/130) ([ralfzen](https://github.com/ralfzen))
- Fix directory structure mistake for BiFrost docs deploy [\#129](https://github.com/buildlyio/buildly-core/pull/129) ([lemkeb](https://github.com/lemkeb))
- Data mesh joinrecord endpoints PLAT-464 [\#128](https://github.com/buildlyio/buildly-core/pull/128) ([ralfzen](https://github.com/ralfzen))
- Data mesh models - PLAT-464 [\#127](https://github.com/buildlyio/buildly-core/pull/127) ([ralfzen](https://github.com/ralfzen))
- Django update [\#126](https://github.com/buildlyio/buildly-core/pull/126) ([ralfzen](https://github.com/ralfzen))

## [0.1.4](https://github.com/buildlyio/buildly-core/tree/0.1.4) (2019-06-04)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.1.3...0.1.4)

**Merged pull requests:**

- Add UUIDPrimaryKeyRelatedField to CoreGroupSerializer [\#123](https://github.com/buildlyio/buildly-core/pull/123) ([ralfzen](https://github.com/ralfzen))
- Rename Organization.uuid back to organization\_uuid [\#122](https://github.com/buildlyio/buildly-core/pull/122) ([ralfzen](https://github.com/ralfzen))
- Organization PK to UUID - PLAT-481 [\#120](https://github.com/buildlyio/buildly-core/pull/120) ([ralfzen](https://github.com/ralfzen))
- PLAT-429: fixing retrieving URL for caching for multipart response [\#119](https://github.com/buildlyio/buildly-core/pull/119) ([docktorrr](https://github.com/docktorrr))
- Revert "PLAT-429: cache responses from duplicated logic module requests" [\#117](https://github.com/buildlyio/buildly-core/pull/117) ([ralfzen](https://github.com/ralfzen))

## [0.1.3](https://github.com/buildlyio/buildly-core/tree/0.1.3) (2019-05-28)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.1.2...0.1.3)

**Merged pull requests:**

- Change primary\_key to level2\_uuid in WorkflowLevel2 - CU-631 [\#116](https://github.com/buildlyio/buildly-core/pull/116) ([ralfzen](https://github.com/ralfzen))
- Narrative shift [\#115](https://github.com/buildlyio/buildly-core/pull/115) ([lemkeb](https://github.com/lemkeb))
- PLAT-459: fix swagger type [\#114](https://github.com/buildlyio/buildly-core/pull/114) ([docktorrr](https://github.com/docktorrr))
- PLAT-457: default value for DEFAULT\_ORG env var [\#112](https://github.com/buildlyio/buildly-core/pull/112) ([docktorrr](https://github.com/docktorrr))
- Enable customizable password validation CU-620 [\#111](https://github.com/buildlyio/buildly-core/pull/111) ([ralfzen](https://github.com/ralfzen))
- PLAT-456: disable schema for API gateway view [\#110](https://github.com/buildlyio/buildly-core/pull/110) ([docktorrr](https://github.com/docktorrr))
- WAL-417: notify after build in drone [\#109](https://github.com/buildlyio/buildly-core/pull/109) ([docktorrr](https://github.com/docktorrr))
- WAL-417: drone notification to walhall webhook [\#108](https://github.com/buildlyio/buildly-core/pull/108) ([docktorrr](https://github.com/docktorrr))
- Add PKRelatedField for WFLType - CU-583 [\#107](https://github.com/buildlyio/buildly-core/pull/107) ([ralfzen](https://github.com/ralfzen))
- Add pagination to WFL2 by default - CU-605 [\#106](https://github.com/buildlyio/buildly-core/pull/106) ([ralfzen](https://github.com/ralfzen))
- Add DateRangeFilter for WFL2 CU-600 [\#105](https://github.com/buildlyio/buildly-core/pull/105) ([ralfzen](https://github.com/ralfzen))
- Add core\_groups to filter\_horizontal [\#104](https://github.com/buildlyio/buildly-core/pull/104) ([ralfzen](https://github.com/ralfzen))
- Extend admins [\#102](https://github.com/buildlyio/buildly-core/pull/102) ([ralfzen](https://github.com/ralfzen))
- PLAT-429: query LogicModule SQL once [\#101](https://github.com/buildlyio/buildly-core/pull/101) ([docktorrr](https://github.com/docktorrr))

## [0.1.2](https://github.com/buildlyio/buildly-core/tree/0.1.2) (2019-05-10)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.1.1...0.1.2)

**Merged pull requests:**

- PLAT-429: cache swagger schema during request and small refactoring [\#113](https://github.com/buildlyio/buildly-core/pull/113) ([docktorrr](https://github.com/docktorrr))
- New fields workflowlevel2 CU-583 [\#103](https://github.com/buildlyio/buildly-core/pull/103) ([ralfzen](https://github.com/ralfzen))
- Fix for serializing M2M-fields of bifrost models [\#100](https://github.com/buildlyio/buildly-core/pull/100) ([ralfzen](https://github.com/ralfzen))
- Add username to refresh token payload CU-515 [\#99](https://github.com/buildlyio/buildly-core/pull/99) ([ralfzen](https://github.com/ralfzen))
- Add JWT payload to refresh\_token CU-515 [\#98](https://github.com/buildlyio/buildly-core/pull/98) ([ralfzen](https://github.com/ralfzen))
- update CoreGroup str method and admin [\#97](https://github.com/buildlyio/buildly-core/pull/97) ([docktorrr](https://github.com/docktorrr))
- PLAT-394: Split workflow views [\#96](https://github.com/buildlyio/buildly-core/pull/96) ([docktorrr](https://github.com/docktorrr))
- PLAT-410: make core\_groups field editable in core user endpoint [\#95](https://github.com/buildlyio/buildly-core/pull/95) ([docktorrr](https://github.com/docktorrr))
- Remove branch condition from drone file [\#94](https://github.com/buildlyio/buildly-core/pull/94) ([docktorrr](https://github.com/docktorrr))
- PLAT-409: Default group [\#93](https://github.com/buildlyio/buildly-core/pull/93) ([docktorrr](https://github.com/docktorrr))
- PLAT-408: update WFL1 permission logic [\#92](https://github.com/buildlyio/buildly-core/pull/92) ([docktorrr](https://github.com/docktorrr))
- Add environment setting for Token expiration time - CU-515 [\#91](https://github.com/buildlyio/buildly-core/pull/91) ([ralfzen](https://github.com/ralfzen))
- Update drone file to deploy documentation [\#90](https://github.com/buildlyio/buildly-core/pull/90) ([jefmoura](https://github.com/jefmoura))
- PLAT-385: Update coregroup endpoint [\#89](https://github.com/buildlyio/buildly-core/pull/89) ([docktorrr](https://github.com/docktorrr))
- PLAT-377 - Add endpoint name [\#88](https://github.com/buildlyio/buildly-core/pull/88) ([jefmoura](https://github.com/jefmoura))
- fix core user creation in admin [\#87](https://github.com/buildlyio/buildly-core/pull/87) ([docktorrr](https://github.com/docktorrr))
- fix CoreUser admin [\#86](https://github.com/buildlyio/buildly-core/pull/86) ([docktorrr](https://github.com/docktorrr))
- Add documentation folder for docs site contents [\#85](https://github.com/buildlyio/buildly-core/pull/85) ([lemkeb](https://github.com/lemkeb))
- PLAT-165: refactor permission classes [\#84](https://github.com/buildlyio/buildly-core/pull/84) ([docktorrr](https://github.com/docktorrr))
- PLAT-165: remove Group viewset and serializer [\#83](https://github.com/buildlyio/buildly-core/pull/83) ([docktorrr](https://github.com/docktorrr))
- PLAT-165: Change CoreGroup model [\#82](https://github.com/buildlyio/buildly-core/pull/82) ([docktorrr](https://github.com/docktorrr))
- PLAT-367: back to the normal migrations in entrypoint [\#81](https://github.com/buildlyio/buildly-core/pull/81) ([docktorrr](https://github.com/docktorrr))
- Get back core\_user.id field in serializer [\#78](https://github.com/buildlyio/buildly-core/pull/78) ([docktorrr](https://github.com/docktorrr))

## [0.1.1](https://github.com/buildlyio/buildly-core/tree/0.1.1) (2019-03-27)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.1.0...0.1.1)

**Merged pull requests:**

- PLAT-367: make fake migrations in entrypoint \(temporally\) [\#80](https://github.com/buildlyio/buildly-core/pull/80) ([docktorrr](https://github.com/docktorrr))
- PLAT-367: resetting workflow migrations [\#79](https://github.com/buildlyio/buildly-core/pull/79) ([docktorrr](https://github.com/docktorrr))
- PLAT-349: fix oauth user endpoint [\#76](https://github.com/buildlyio/buildly-core/pull/76) ([docktorrr](https://github.com/docktorrr))
- PLAT-349: fix workflow-user migration [\#75](https://github.com/buildlyio/buildly-core/pull/75) ([docktorrr](https://github.com/docktorrr))
- PLAT-349: fix user migrations [\#74](https://github.com/buildlyio/buildly-core/pull/74) ([docktorrr](https://github.com/docktorrr))

## [0.1.0](https://github.com/buildlyio/buildly-core/tree/0.1.0) (2019-03-22)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.0.5...0.1.0)

**Merged pull requests:**

- PLAT-349: fix oauth user endpoint [\#77](https://github.com/buildlyio/buildly-core/pull/77) ([docktorrr](https://github.com/docktorrr))
- PLAT-349: fix migration [\#73](https://github.com/buildlyio/buildly-core/pull/73) ([docktorrr](https://github.com/docktorrr))
- PLAT-349: fix migration core\_user unique constraint migration [\#72](https://github.com/buildlyio/buildly-core/pull/72) ([docktorrr](https://github.com/docktorrr))
- Update .drone.yml [\#71](https://github.com/buildlyio/buildly-core/pull/71) ([jefmoura](https://github.com/jefmoura))
- Remove branch name from drone pipeline for now [\#70](https://github.com/buildlyio/buildly-core/pull/70) ([jefmoura](https://github.com/jefmoura))
- PLAT-160: Permissions minor refactoring [\#69](https://github.com/buildlyio/buildly-core/pull/69) ([docktorrr](https://github.com/docktorrr))
- PLAT-350: User refactoring [\#68](https://github.com/buildlyio/buildly-core/pull/68) ([docktorrr](https://github.com/docktorrr))
-  PLAT-350: Replace User with CoreUser [\#67](https://github.com/buildlyio/buildly-core/pull/67) ([docktorrr](https://github.com/docktorrr))
- WAL-154 - Create new step to use new docker registry structure [\#66](https://github.com/buildlyio/buildly-core/pull/66) ([jefmoura](https://github.com/jefmoura))
-  PLAT-350: fixing migration [\#65](https://github.com/buildlyio/buildly-core/pull/65) ([docktorrr](https://github.com/docktorrr))
-  PLAT-350: Custom user model [\#64](https://github.com/buildlyio/buildly-core/pull/64) ([docktorrr](https://github.com/docktorrr))
- Group names migration [\#63](https://github.com/buildlyio/buildly-core/pull/63) ([docktorrr](https://github.com/docktorrr))
-  PLAT-165: CoreGroup for model-level permissions   [\#56](https://github.com/buildlyio/buildly-core/pull/56) ([docktorrr](https://github.com/docktorrr))

## [0.0.5](https://github.com/buildlyio/buildly-core/tree/0.0.5) (2019-03-12)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.0.4...0.0.5)

**Merged pull requests:**

- Remove fixed id assignment of initial auth.Groups [\#62](https://github.com/buildlyio/buildly-core/pull/62) ([ralfzen](https://github.com/ralfzen))
- Clear up default email-email-template-test [\#61](https://github.com/buildlyio/buildly-core/pull/61) ([ralfzen](https://github.com/ralfzen))
- Add default organization for pw-reset-email-lookup [\#60](https://github.com/buildlyio/buildly-core/pull/60) ([ralfzen](https://github.com/ralfzen))
- Fix social auth [\#58](https://github.com/buildlyio/buildly-core/pull/58) ([jefmoura](https://github.com/jefmoura))
- Improve social auth [\#57](https://github.com/buildlyio/buildly-core/pull/57) ([jefmoura](https://github.com/jefmoura))
- Use tcp port wait script in production [\#55](https://github.com/buildlyio/buildly-core/pull/55) ([jefmoura](https://github.com/jefmoura))
- Fix drone config removing matrix [\#52](https://github.com/buildlyio/buildly-core/pull/52) ([jefmoura](https://github.com/jefmoura))
- EndpointNotFoundException w/ path and METHOD [\#51](https://github.com/buildlyio/buildly-core/pull/51) ([ralfzen](https://github.com/ralfzen))
- PLAT-328: change password reset token validation response [\#50](https://github.com/buildlyio/buildly-core/pull/50) ([docktorrr](https://github.com/docktorrr))
- Create LICENSE [\#49](https://github.com/buildlyio/buildly-core/pull/49) ([glind](https://github.com/glind))
- define swagger schema for custom CoureUser endpoints [\#48](https://github.com/buildlyio/buildly-core/pull/48) ([docktorrr](https://github.com/docktorrr))
- add endpoint for reset password request validation [\#47](https://github.com/buildlyio/buildly-core/pull/47) ([docktorrr](https://github.com/docktorrr))
- Custom templating for resetting password [\#46](https://github.com/buildlyio/buildly-core/pull/46) ([docktorrr](https://github.com/docktorrr))
- Update OAuth env var name [\#44](https://github.com/buildlyio/buildly-core/pull/44) ([jefmoura](https://github.com/jefmoura))
- PLAT-191: Reset password [\#43](https://github.com/buildlyio/buildly-core/pull/43) ([docktorrr](https://github.com/docktorrr))
- PLAT-167: workflow views refactoring [\#42](https://github.com/buildlyio/buildly-core/pull/42) ([docktorrr](https://github.com/docktorrr))
- PLAT-166: remove unused or redundant fields in serializers [\#41](https://github.com/buildlyio/buildly-core/pull/41) ([docktorrr](https://github.com/docktorrr))
- PLAT-162: remove unused templates and web forms [\#40](https://github.com/buildlyio/buildly-core/pull/40) ([docktorrr](https://github.com/docktorrr))
- PLAT-283: pep8 fixes [\#39](https://github.com/buildlyio/buildly-core/pull/39) ([docktorrr](https://github.com/docktorrr))
- add invitation links to the response [\#38](https://github.com/buildlyio/buildly-core/pull/38) ([docktorrr](https://github.com/docktorrr))
- Add GitHub PR template [\#37](https://github.com/buildlyio/buildly-core/pull/37) ([jefmoura](https://github.com/jefmoura))
- Handle empty relationship when trying to aggregate - PLAT-278 [\#36](https://github.com/buildlyio/buildly-core/pull/36) ([ralfzen](https://github.com/ralfzen))
- Test for query-filter-fix in Data Mesh [\#35](https://github.com/buildlyio/buildly-core/pull/35) ([ralfzen](https://github.com/ralfzen))
- PLAT-219 - Implementation of Social auth [\#34](https://github.com/buildlyio/buildly-core/pull/34) ([jefmoura](https://github.com/jefmoura))
- Ignore case sensitivity in aggregate query argument [\#32](https://github.com/buildlyio/buildly-core/pull/32) ([ralfzen](https://github.com/ralfzen))
- PLAT-161 - Improve celery conf [\#22](https://github.com/buildlyio/buildly-core/pull/22) ([jefmoura](https://github.com/jefmoura))

## [0.0.4](https://github.com/buildlyio/buildly-core/tree/0.0.4) (2019-02-14)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.0.3...0.0.4)

**Merged pull requests:**

- Fix query-filters in Data Mesh [\#33](https://github.com/buildlyio/buildly-core/pull/33) ([ralfzen](https://github.com/ralfzen))
- PLAT-160: Refactor tests final [\#31](https://github.com/buildlyio/buildly-core/pull/31) ([docktorrr](https://github.com/docktorrr))
- PLAT-160: fix tests for milestones and internationalization [\#30](https://github.com/buildlyio/buildly-core/pull/30) ([docktorrr](https://github.com/docktorrr))
- PLAT-160: refactor organization and fix tests for it [\#29](https://github.com/buildlyio/buildly-core/pull/29) ([docktorrr](https://github.com/docktorrr))
- Minimal approach on data mesh [\#28](https://github.com/buildlyio/buildly-core/pull/28) ([ralfzen](https://github.com/ralfzen))
- PLAT-160: fix tests for portfolio, change tola\_user to core\_user [\#27](https://github.com/buildlyio/buildly-core/pull/27) ([docktorrr](https://github.com/docktorrr))
- PLAT-160: fix tests for auth and workflow team [\#26](https://github.com/buildlyio/buildly-core/pull/26) ([docktorrr](https://github.com/docktorrr))
- PLAT-160: fix tests for workflow level 2, rename permission class [\#25](https://github.com/buildlyio/buildly-core/pull/25) ([docktorrr](https://github.com/docktorrr))
- PLAT-160: fix tests for workflow level 1 viewset [\#24](https://github.com/buildlyio/buildly-core/pull/24) ([docktorrr](https://github.com/docktorrr))
- Catch EndpointNotFoundException instead of all GatewayErrors [\#23](https://github.com/buildlyio/buildly-core/pull/23) ([ralfzen](https://github.com/ralfzen))
- Fix missing request when validating Bifrost objects - PLAT-202 [\#20](https://github.com/buildlyio/buildly-core/pull/20) ([ralfzen](https://github.com/ralfzen))
- Clear exception for endpoint not found [\#19](https://github.com/buildlyio/buildly-core/pull/19) ([ralfzen](https://github.com/ralfzen))
- PLAT-265 - Return raw data when processed one isn't available [\#18](https://github.com/buildlyio/buildly-core/pull/18) ([jefmoura](https://github.com/jefmoura))
-  Rename user\_uuid to core\_user\_uuid in jwt\_enricher - PLAT-146 [\#17](https://github.com/buildlyio/buildly-core/pull/17) ([ralfzen](https://github.com/ralfzen))
- Add test script for pytest with idpb [\#16](https://github.com/buildlyio/buildly-core/pull/16) ([ralfzen](https://github.com/ralfzen))
- PLAT-254 - Make SECRET\_KEY mandatory [\#15](https://github.com/buildlyio/buildly-core/pull/15) ([Menda](https://github.com/Menda))
- Remove unused PrimJSONEncoder - PLAT-243 [\#13](https://github.com/buildlyio/buildly-core/pull/13) ([ralfzen](https://github.com/ralfzen))
- Fix encoding responses is removing UUIDs - PLAT-243 [\#12](https://github.com/buildlyio/buildly-core/pull/12) ([ralfzen](https://github.com/ralfzen))
- Small improvements [\#11](https://github.com/buildlyio/buildly-core/pull/11) ([ralfzen](https://github.com/ralfzen))
- Add authorization to Bifrost aggregated data - PLAT-202 [\#10](https://github.com/buildlyio/buildly-core/pull/10) ([ralfzen](https://github.com/ralfzen))
- Update Coreuser serializer [\#9](https://github.com/buildlyio/buildly-core/pull/9) ([jefmoura](https://github.com/jefmoura))
- Allow anybody to create a new user [\#8](https://github.com/buildlyio/buildly-core/pull/8) ([jefmoura](https://github.com/jefmoura))
- PLAT-203 - Aggregate multiple objects [\#7](https://github.com/buildlyio/buildly-core/pull/7) ([jefmoura](https://github.com/jefmoura))
- Allow only superusers to use LogicModules endpoint - PLAT-180 [\#6](https://github.com/buildlyio/buildly-core/pull/6) ([ralfzen](https://github.com/ralfzen))
- PLAT-190 Fetch data for Bifrost relationships [\#5](https://github.com/buildlyio/buildly-core/pull/5) ([jefmoura](https://github.com/jefmoura))
- PLAT 184: Add registration [\#4](https://github.com/buildlyio/buildly-core/pull/4) ([docktorrr](https://github.com/docktorrr))
- Add registration process [\#3](https://github.com/buildlyio/buildly-core/pull/3) ([docktorrr](https://github.com/docktorrr))
- PLAT-178 - Aggregate data from external services [\#2](https://github.com/buildlyio/buildly-core/pull/2) ([jefmoura](https://github.com/jefmoura))
- PLAT-174 - Create relationship field in LogicModule [\#1](https://github.com/buildlyio/buildly-core/pull/1) ([jefmoura](https://github.com/jefmoura))

## [0.0.3](https://github.com/buildlyio/buildly-core/tree/0.0.3) (2019-01-25)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.0.2...0.0.3)

## [0.0.2](https://github.com/buildlyio/buildly-core/tree/0.0.2) (2019-01-16)
[Full Changelog](https://github.com/buildlyio/buildly-core/compare/0.0.1...0.0.2)

## [0.0.1](https://github.com/buildlyio/buildly-core/tree/0.0.1) (2018-12-20)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*