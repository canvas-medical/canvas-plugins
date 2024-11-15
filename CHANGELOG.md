# CHANGELOG


## v0.4.0 (2024-11-12)

### Chores

* chore: improve mypy configuration and fix the resulting errors (#187) ([`44071f1`](https://github.com/canvas-medical/canvas-plugins/commit/44071f13f069027d1d1fdadc932fe167010591ac))

* chore: bump the development-patches group across 1 directory with 2 updates (#182) ([`babb355`](https://github.com/canvas-medical/canvas-plugins/commit/babb3556ef487fb546319e526fca519ea6c6dbd8))

* chore: bump django from 5.1.2 to 5.1.3 in the production-patches group (#179) ([`163540a`](https://github.com/canvas-medical/canvas-plugins/commit/163540a7b833e52f5fa50a17f595fda1e1adaa63))

### Code Style

* style: use pathlib to construct a path (#176) ([`12e7c49`](https://github.com/canvas-medical/canvas-plugins/commit/12e7c49a04d25bf8767f856b53c1506870992349))

### Features

* feat: adds more lab related models (#130)

Signed-off-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com>
Co-authored-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com> ([`6177e00`](https://github.com/canvas-medical/canvas-plugins/commit/6177e00a32f24e314c80aa6223249a341a745835))

* feat: adds imaging models (#137) ([`84c63e2`](https://github.com/canvas-medical/canvas-plugins/commit/84c63e2cb1225f1c481ea7b59d5fb2963afba08b))

* feat: add plugin_created and plugin_updated events (#178) ([`efd45e2`](https://github.com/canvas-medical/canvas-plugins/commit/efd45e281e6d63ba0c8865e92e5521186df476b3))

* feat: add is_predictive property to cqm class meta (#181) ([`9ff3117`](https://github.com/canvas-medical/canvas-plugins/commit/9ff3117a0758d17d7381e39721dcbdbc7ea12f12))


## v0.3.1 (2024-10-31)

### Bug Fixes

* fix: valueSet query (#175) ([`3b4d7b5`](https://github.com/canvas-medical/canvas-plugins/commit/3b4d7b53c6a385ebd862d15cf8a3b8b0a7af0d36))

### Chores

* chore: local development improvements (#102)

Co-authored-by: José Magalhães <jose.magalhaes@canvasmedical.com> ([`ca4458e`](https://github.com/canvas-medical/canvas-plugins/commit/ca4458e59ee51abf638facb8eb9ff231be0efa18))

* chore: fix test distribution step on semantic release gh action (#173) ([`6ee6b0c`](https://github.com/canvas-medical/canvas-plugins/commit/6ee6b0c715b771072a9a81b91bc7cc7f7bcb16e7))


## v0.3.0 (2024-10-29)

### Bug Fixes

* fix: pull out meta properties of CQM protocols without importing file (#140) ([`1402f8e`](https://github.com/canvas-medical/canvas-plugins/commit/1402f8ea35107dbc0900dd6aad48cb5a0ac9aebd))

### Chores

* chore: bump keyring from 25.4.1 to 25.5.0 (#170) ([`c7ca11d`](https://github.com/canvas-medical/canvas-plugins/commit/c7ca11d5d262a2a1b4b9808ef0fef834b3523fd7))

* chore: bump grpcio-tools from 1.62.0 to 1.62.3 in the development-minors group (#168) ([`755f741`](https://github.com/canvas-medical/canvas-plugins/commit/755f741562b2bde3e69df44f85aeee1b90bd4290))

* chore: bump grpcio from 1.67.0 to 1.67.1 in the production-patches group (#172) ([`22c5bc3`](https://github.com/canvas-medical/canvas-plugins/commit/22c5bc33ac21b77e7b0854abeb5f2cc2dcb12ace))

* chore: bump pydantic from 2.6.1 to 2.9.2 (#164) ([`14d4be1`](https://github.com/canvas-medical/canvas-plugins/commit/14d4be1ee7f4051eb7f7bb19bee15d5a7402674d))

* chore: bump keyring from 24.3.0 to 25.4.1 (#157) ([`23327a5`](https://github.com/canvas-medical/canvas-plugins/commit/23327a5cab5621e9471aa1f2f0871946e8a44921))

* chore: bump grpcio from 1.62.0 to 1.67.0 (#165) ([`030048d`](https://github.com/canvas-medical/canvas-plugins/commit/030048df188566822e2ce0f6de4ea0e354aec0ce))

* chore: bump pyjwt from 2.4.0 to 2.9.0 (#167) ([`594dc74`](https://github.com/canvas-medical/canvas-plugins/commit/594dc74ca88244307a6e43230ad9a75ec57dfc43))

* chore: bump ipython from 8.21.0 to 8.29.0 (#159) ([`54d2651`](https://github.com/canvas-medical/canvas-plugins/commit/54d265186e2cc679fdbc240dd7405964c594673c))

* chore: auto-update pre-commit hooks (#146) ([`b0bfb46`](https://github.com/canvas-medical/canvas-plugins/commit/b0bfb46a14d5133894310641618fa3f97b45064e))

* chore: bump typer from 0.9.0 to 0.12.5 (#162) ([`cb6af5c`](https://github.com/canvas-medical/canvas-plugins/commit/cb6af5c3a76a1326388604edd62e82186a0ee888))

* chore: bump restrictedpython from 7.3 to 7.4 (#166) ([`1acb504`](https://github.com/canvas-medical/canvas-plugins/commit/1acb504469b0c6ae99f3ae3d2f41eacefeb3a80a))

* chore: bump redis from 5.0.4 to 5.2.0 (#161) ([`fe40619`](https://github.com/canvas-medical/canvas-plugins/commit/fe4061918e49173a7aecb8a7312f7f39e064005c))

* chore: bump typing-extensions from 4.8.0 to 4.12.2 (#158) ([`47c4add`](https://github.com/canvas-medical/canvas-plugins/commit/47c4add0920124dabbdddff43bbb253cd15281d2))

* chore: bump protobuf from 4.25.3 to 4.25.5 (#156) ([`85e23dd`](https://github.com/canvas-medical/canvas-plugins/commit/85e23dd61247ad1db45b82f4a8db48ddbabeae87))

* chore: bump jsonschema from 4.21.1 to 4.23.0 (#163) ([`5be8644`](https://github.com/canvas-medical/canvas-plugins/commit/5be8644a9a0befbcc7806be5b424164b51f366ad))

* chore: bump websocket-client from 1.7.0 to 1.8.0 (#160) ([`28b4389`](https://github.com/canvas-medical/canvas-plugins/commit/28b43891394312fd92af84d86e49f1a2095708a3))

* chore: bump the development-minors group with 8 updates (#154) ([`24b4d9a`](https://github.com/canvas-medical/canvas-plugins/commit/24b4d9aaee3209e60266caf973e2ac6a28369f09))

* chore: bump peter-evans/create-pull-request from 4 to 7 (#151) ([`47e6c8f`](https://github.com/canvas-medical/canvas-plugins/commit/47e6c8f96cb535f0aa81fd976a108e02d7c8182b))

* chore: bump the production-patches group with 3 updates (#153) ([`9f3e69a`](https://github.com/canvas-medical/canvas-plugins/commit/9f3e69a79e46672a65830af3f0adac2703dc1191))

* chore: bump pre-commit/action from 3.0.0 to 3.0.1 (#152) ([`3bd3919`](https://github.com/canvas-medical/canvas-plugins/commit/3bd39191efcab214634fbb5b06440d45ff63c8cb))

* chore: bump pre-commit from 3.6.2 to 4.0.1 in the development-majors group (#155) ([`6eb777b`](https://github.com/canvas-medical/canvas-plugins/commit/6eb777b695edd79f291a763d5466a7b22316cf07))

* chore: add dependabot config (#150) ([`f8841fd`](https://github.com/canvas-medical/canvas-plugins/commit/f8841fdcae718da368a588c9630fa9844318aa5f))

* chore: enhance release process by installing and executing the distribution (#143) ([`2d2352d`](https://github.com/canvas-medical/canvas-plugins/commit/2d2352d7354599a6bad15a7820a8c1d217144a6a))

* chore: auto-update pre-commit hooks (#142) ([`d4aff18`](https://github.com/canvas-medical/canvas-plugins/commit/d4aff18587a8802f0bd5fcf0f431586a533fd9f9))

* chore: clean up pre-commit-update workflow (#141) ([`2ab0694`](https://github.com/canvas-medical/canvas-plugins/commit/2ab0694215d6463e3e556dd76ae4f2dbc50e597f))

* chore: improve generate-protobufs script (#135) ([`61597ab`](https://github.com/canvas-medical/canvas-plugins/commit/61597abea8cf16248c422657cbfa6632a056b396))

* chore: fix pre-commit errors (#138) ([`1da3f33`](https://github.com/canvas-medical/canvas-plugins/commit/1da3f33adda53f73ec114075f1c581218f8e24ea))

* chore(ci): fix pre-commit on CI (#136) ([`ec6b4b3`](https://github.com/canvas-medical/canvas-plugins/commit/ec6b4b3849582bdfcfea9cb605d894b62c9d1bf7))

### Features

* feat: add SDK Questionnaire and Interview models (#104) ([`ba8b556`](https://github.com/canvas-medical/canvas-plugins/commit/ba8b556ee1b36a173ab07ddd4d705d5b131c6fc7))

* feat: add more event types (#139) ([`ffc9c25`](https://github.com/canvas-medical/canvas-plugins/commit/ffc9c255181da5a95a0bd4e1535c988e40e39761))

* feat: add protocol classname to effects and include in plugin_runner event handler (#145) ([`517cadb`](https://github.com/canvas-medical/canvas-plugins/commit/517cadb18fc09ded585b74975edc74283acb7040))

* feat: add feedback_enabled property to protocol card effect (#148) ([`5dd7d96`](https://github.com/canvas-medical/canvas-plugins/commit/5dd7d963fd36a627c6072c8ead83e76eaa8ad950))

* feat: clipboard command events (#147) ([`eaf339a`](https://github.com/canvas-medical/canvas-plugins/commit/eaf339a1656978b04c16e4453d96c77c9ca868df))


## v0.2.11 (2024-10-15)

### Bug Fixes

* fix: fix settings error in canvas-cli (#133)

* Adds settings to pyproject.toml.

* Adds .py extension to settings in pyproject.toml. ([`52e4438`](https://github.com/canvas-medical/canvas-plugins/commit/52e4438d57627b2e397ab2b2085e0a5579741f55))

### Chores

* chore: fix semantic release workflow (#134) ([`97a5069`](https://github.com/canvas-medical/canvas-plugins/commit/97a5069d8eeda5c8f455c531feb5c1a40e4fb487))

* chore(docs): add CONTRIBUTING.md and CODE_OF_CONDUCT.md (#132)

chore(docs): add CONTRIBUTING and CODE_OF_CONDUCT ([`365751b`](https://github.com/canvas-medical/canvas-plugins/commit/365751b186d8d20454cf059b749f9ebdcd3ebd56))

* chore: fix semantic-release publish (#129) ([`8a24339`](https://github.com/canvas-medical/canvas-plugins/commit/8a24339455bb58246c78d2670b02465207991a4f))


## v0.2.10 (2024-10-14)

### Bug Fixes

* fix: improvements to the TaskCommand definition ([`1dbc4ee`](https://github.com/canvas-medical/canvas-plugins/commit/1dbc4eec4b0a58f264035f55c296054cbb7638e8))

### Chores

* chore: fix semantic release (#128) ([`d4bbcc7`](https://github.com/canvas-medical/canvas-plugins/commit/d4bbcc737f08cd528b09a71a23cc6deabc427d66))

* chore(ci): add automated releases using semantic release (#127) ([`2f830c8`](https://github.com/canvas-medical/canvas-plugins/commit/2f830c8cfb4436b34502d457456e97b487e9c122))

* chore: bump restrictedpython from 7.1 to 7.3 (#117)

Bump restrictedpython from 7.1 to 7.3

Bumps [restrictedpython](https://github.com/zopefoundation/RestrictedPython) from 7.1 to 7.3.
- [Changelog](https://github.com/zopefoundation/RestrictedPython/blob/master/CHANGES.rst)
- [Commits](https://github.com/zopefoundation/RestrictedPython/compare/7.1...7.3)

---
updated-dependencies:
- dependency-name: restrictedpython
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`ad5ccea`](https://github.com/canvas-medical/canvas-plugins/commit/ad5ccead18b238d809a4d9082d4ae4a14a439956))

* chore: add pull request title validator (#126) ([`194bf0b`](https://github.com/canvas-medical/canvas-plugins/commit/194bf0b56c5c036de853ed149a702eecf7ec3af5))

* chore(ci): improve build and test workflow (#125) ([`5c15020`](https://github.com/canvas-medical/canvas-plugins/commit/5c1502037c1448f700657091c21e92513270a6eb))

### Unknown

* Create CQM protocol subclass  (#120)

* create cqm subclass and create way of extracting meta properties for home-app ([`316af87`](https://github.com/canvas-medical/canvas-plugins/commit/316af873f39bab3d4e84669c72156c05df84c4f6))

* Merge pull request #123 from canvas-medical/fix/improve-task-command-definition

fix: improvements to the TaskCommand definition ([`bca6801`](https://github.com/canvas-medical/canvas-plugins/commit/bca68016b777e11316809345bee19991b93c8279))


## v0.2.9 (2024-10-08)

### Bug Fixes

* fix: improve AllergyCommand definition ([`049c16d`](https://github.com/canvas-medical/canvas-plugins/commit/049c16dc00aba1c13726855c42f6de0797c2e49f))

* fix: add MedicalHistoryCommand to __init__ ([`0b91465`](https://github.com/canvas-medical/canvas-plugins/commit/0b91465ada1dbbb1d3038d2e4aec07d2b8f85362))

### Unknown

* Merge pull request #122 from canvas-medical/feature/jw-koala-2047

Adds database parsing and addition to settings. ([`c775189`](https://github.com/canvas-medical/canvas-plugins/commit/c7751898c74ed0bd03886f961416509f91ce705b))

* Apply suggestions from code review ([`613b47e`](https://github.com/canvas-medical/canvas-plugins/commit/613b47e83c62f673b448c22b3b90c7e672646eac))

* Changes database URL function. ([`1ccc659`](https://github.com/canvas-medical/canvas-plugins/commit/1ccc65963f9a2767964b6d38d71e7ed16354130c))

* Simplifies url parsing. ([`6eb1424`](https://github.com/canvas-medical/canvas-plugins/commit/6eb142413dd1ac0008c5e9d85094112be5e32075))

* Adds database parsing and addition to settings. ([`b5574dc`](https://github.com/canvas-medical/canvas-plugins/commit/b5574dcb5f2dda543374beb0c23875cf958873dd))

* Merge pull request #121 from canvas-medical/fix/improve-allergy-command

fix: improve AllergyCommand definition ([`63b975f`](https://github.com/canvas-medical/canvas-plugins/commit/63b975f3a625a07ace21936e5952456e6d605b83))

* Merge pull request #109 from canvas-medical/feat/koala-1925-close-goal

feat: add CloseGoal command SDK definition ([`e2b8ad8`](https://github.com/canvas-medical/canvas-plugins/commit/e2b8ad8a685f64cf6ba2afed4e68132a0ca63acb))

* Merge branch 'main' into feat/koala-1925-close-goal

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`2e202d5`](https://github.com/canvas-medical/canvas-plugins/commit/2e202d5fa475197a42cf7974500ec3915d0b46c6))

* Merge pull request #107 from canvas-medical/feat/koala-1924-change-diagnosis

feat: add UpdateDiagnosis command SDK definition ([`fc00b73`](https://github.com/canvas-medical/canvas-plugins/commit/fc00b736e93fcd790858ba154490ad4f0a680422))

* Merge branch 'main' into feat/koala-1924-change-diagnosis

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`7fc80d4`](https://github.com/canvas-medical/canvas-plugins/commit/7fc80d4a4e441b69438b96c1243c7ded75a4cb11))

* Merge pull request #106 from canvas-medical/feat/koala-1923-vitals

feat: add Vitals command SDK definition ([`0217f94`](https://github.com/canvas-medical/canvas-plugins/commit/0217f945e5ae4df6cf68efeb09dba9e4834837a6))

* small improvements ([`ded0021`](https://github.com/canvas-medical/canvas-plugins/commit/ded0021128b55ca8926f3e7c4b1b3e75e8dfac55))

* Merge branch 'main' into feat/koala-1923-vitals

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`681a6a3`](https://github.com/canvas-medical/canvas-plugins/commit/681a6a352a502ea5c632a646f85f862525e1e290))

* Merge pull request #105 from canvas-medical/feat/koala-1922-refill

feat: add Refill command SDK definition ([`b08107b`](https://github.com/canvas-medical/canvas-plugins/commit/b08107b6373744deab13dd839ba6ab1c2c819f23))

* fix tests ([`d669649`](https://github.com/canvas-medical/canvas-plugins/commit/d669649e6ce31fdd35d5d191f5e9735adcf23343))

* Merge branch 'main' into feat/koala-1922-refill

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`272c6f4`](https://github.com/canvas-medical/canvas-plugins/commit/272c6f4b622b28ce5ab2918c9d86fd1f3654679a))

* Merge pull request #103 from canvas-medical/feat/koala-1921-task

feat: add Task command SDK definition ([`e484d58`](https://github.com/canvas-medical/canvas-plugins/commit/e484d585d0b253d10b89c8256e73d3638d0df49e))

* Merge branch 'main' into feat/koala-1921-task

# Conflicts:
#	canvas_generated/messages/effects_pb2.py
#	canvas_generated/messages/effects_pb2.pyi
#	protobufs/canvas_generated/messages/effects.proto ([`351367f`](https://github.com/canvas-medical/canvas-plugins/commit/351367f451e559f3a6ce1f1a6386658b2fd9ecb9))

* Merge pull request #101 from canvas-medical/feat/koala-1917-medical-history

feat: add MedicationHistory command SDK definition ([`e38bee7`](https://github.com/canvas-medical/canvas-plugins/commit/e38bee74c4543f9f11d7828a137a1116c407df1d))

* Merge branch 'main' into feat/koala-1917-medical-history

# Conflicts:
#	canvas_generated/messages/effects_pb2.py
#	canvas_generated/messages/effects_pb2.pyi ([`0fc9369`](https://github.com/canvas-medical/canvas-plugins/commit/0fc9369d2a7301576479445e1a26e935a32e5eaa))

* Merge pull request #100 from canvas-medical/feat/koala-1916-surgical-history

feat: add PastSurgicalHistory command SDK definition ([`e65477e`](https://github.com/canvas-medical/canvas-plugins/commit/e65477e831eeb4d76606c712e16e6225366ea0f2))

* Merge branch 'main' into feat/koala-1916-surgical-history

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`34d5b0d`](https://github.com/canvas-medical/canvas-plugins/commit/34d5b0de6f1263872918146d2959f56149b89731))

* Merge pull request #99 from canvas-medical/feat/koala-1915-remove-allergy

feat: add RemoveAllergy command SDK definition ([`2c1c339`](https://github.com/canvas-medical/canvas-plugins/commit/2c1c33939e0828e3d2176e6b3a3743e2f5bfb0ec))

* Merge branch 'main' into feat/koala-1915-remove-allergy

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`ea9f2a2`](https://github.com/canvas-medical/canvas-plugins/commit/ea9f2a216cd4a5dbe9d021dc9f4c11d4c0268662))

* Merge pull request #98 from canvas-medical/feat/koala-1914-allergy

feat: add Allergy command SDK definition ([`e8f9ca1`](https://github.com/canvas-medical/canvas-plugins/commit/e8f9ca163d32efb6d2fff46024fb00ee0690a653))

* Merge branch 'main' into feat/koala-1914-allergy

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`be29b10`](https://github.com/canvas-medical/canvas-plugins/commit/be29b10d42582d6e915bb8f37165a9a407c241dd))

* Merge pull request #97 from canvas-medical/feat/koala-1913-family-history

feat: add FamilyHistory command SDK definition ([`282a9df`](https://github.com/canvas-medical/canvas-plugins/commit/282a9df222e839a4211c4cfb34aa64bb75531a26))

* Merge branch 'main' into feat/koala-1913-family-history

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`2a148ab`](https://github.com/canvas-medical/canvas-plugins/commit/2a148ab4b5402a04806509b2297fb8ff6bc4f8fe))

* Merge pull request #96 from canvas-medical/feat/koala-1909-lab-order

feat: add LabOrder command SDK definition ([`6503060`](https://github.com/canvas-medical/canvas-plugins/commit/650306049d437cabeb8771515cfde58d07be901b))

* Merge branch 'main' into feat/koala-1909-lab-order

# Conflicts:
#	canvas_generated/messages/effects_pb2.py ([`84ec9b3`](https://github.com/canvas-medical/canvas-plugins/commit/84ec9b3835a74174ad2722d8aa4f745995ee675c))


## v0.2.8 (2024-10-02)

### Unknown

* Merge pull request #119 from canvas-medical/feature/jw-add-valueset-import

Adds value_set module to allowed imports. ([`511717c`](https://github.com/canvas-medical/canvas-plugins/commit/511717c0f997f39add12e8b992f1362ade0691b9))

* separate tests out ([`87b5a5f`](https://github.com/canvas-medical/canvas-plugins/commit/87b5a5f2b6fe430aafc9d8bcc542e45edec7bc70))

* Adds value_set module to allowed imports. ([`61123d1`](https://github.com/canvas-medical/canvas-plugins/commit/61123d17d94c7794967a77949ed65cb1c8808bcb))


## v0.2.7 (2024-09-27)

### Features

* feat: add patient_chart_summary_configuration effect and new event to configure patient chart summary (#94)

* add patient_chart_summary_configuration effect and new event to configure patient chart summary

* regen protobufs after rebase ([`f53f61e`](https://github.com/canvas-medical/canvas-plugins/commit/f53f61e6132276ba8a54f51005b4995b9246ff59))

### Unknown

* Merge pull request #108 from canvas-medical/feature/jw-poetry-lock-update

Updates poetry.lock file. ([`eeaafcd`](https://github.com/canvas-medical/canvas-plugins/commit/eeaafcd994ad6c7c73c6f36175c09947fac66d5e))

* Updates poetry.lock file. ([`f74c1d3`](https://github.com/canvas-medical/canvas-plugins/commit/f74c1d37f2e8d7a5ecf0c9b4c647da890dcac5b8))


## v0.2.6 (2024-09-26)

### Chores

* chore: update protobufs ([`549adaa`](https://github.com/canvas-medical/canvas-plugins/commit/549adaaef8a466e41d7be8e470ef1b9d015b0df9))

* chore: add black ad dev dependency ([`4799bae`](https://github.com/canvas-medical/canvas-plugins/commit/4799bae667f2e99f1c557050781d86a491797c7f))

### Features

* feat: add CloseGoal command SDK definition ([`f99b86d`](https://github.com/canvas-medical/canvas-plugins/commit/f99b86d78498dcf16d04861d6674094b943c8165))

* feat: add UpdateDiagnosis command SDK definition ([`f751d07`](https://github.com/canvas-medical/canvas-plugins/commit/f751d074a4758a704c3de2ee4ba69470daf18f0b))

* feat: add Vitals command SDK definition ([`ad56f11`](https://github.com/canvas-medical/canvas-plugins/commit/ad56f1193d58e73b9cf5aef81e9c5787b8879a8e))

* feat: add Refill command SDK definition ([`36b3e1e`](https://github.com/canvas-medical/canvas-plugins/commit/36b3e1e6c259562fa66e9e3ddfdc1c138a087e75))

* feat: add Task command SDK definition ([`4944078`](https://github.com/canvas-medical/canvas-plugins/commit/49440781416d56c8769b2e83ce78bd616e6b6f1a))

* feat: add MedicationHistory command SDK definition ([`e64238d`](https://github.com/canvas-medical/canvas-plugins/commit/e64238d7e1b8f54ccf43ff78248620497cb329b7))

* feat: add PastSurgicalHistory command SDK definition ([`332f898`](https://github.com/canvas-medical/canvas-plugins/commit/332f898fccb7422a495cf1914e5a301ed763a946))

* feat: feat: add RemoveAllergy command SDK definition ([`40fa8d3`](https://github.com/canvas-medical/canvas-plugins/commit/40fa8d3afdb5e2beecac545dfe513dfec24cb6a0))

* feat: add Allergy command SDK definition ([`87f05cf`](https://github.com/canvas-medical/canvas-plugins/commit/87f05cf16813e267b9cba7c8c947cee171dd44fd))

* feat: add FamilyHistory command SDK definition ([`a77fa6d`](https://github.com/canvas-medical/canvas-plugins/commit/a77fa6dcb6f742827955da8c9afa7c1a83636480))

* feat: add LabOrder command SDK definition ([`3348685`](https://github.com/canvas-medical/canvas-plugins/commit/3348685fb28ad9ea010e26c56550e10d545cf53f))

* feat: add instruct and perform commands ([`08997ed`](https://github.com/canvas-medical/canvas-plugins/commit/08997ed5f96bb2971eeed9a179704ffacaab6494))

* feat: add effects for Perform Command ([`b379a28`](https://github.com/canvas-medical/canvas-plugins/commit/b379a289ac483ed1dcc1463b20bb7671aa43ba11))

### Unknown

* Merge pull request #87 from canvas-medical/ad/data-module-orm

Add the django ORM and the first 5 models ([`565a076`](https://github.com/canvas-medical/canvas-plugins/commit/565a07615512eb2852bbeb63cd37f3576c158fbd))

* Merge branch 'main' into ad/data-module-orm ([`c7818bb`](https://github.com/canvas-medical/canvas-plugins/commit/c7818bb80e2749d87e80e4148733dacf7dba966f))

* Make banner alert effects have all optional params and validate on apply (#89)

make banner alert effects have optional params and validate on apply ([`cace864`](https://github.com/canvas-medical/canvas-plugins/commit/cace8645096086181ae0272b074299974dbebeb9))

* Create ProtocolCard Effect (#88) ([`a7b1175`](https://github.com/canvas-medical/canvas-plugins/commit/a7b11758a97f2df985df564389fe25ecb5bd3a05))

* Create CODEOWNERS ([`4f634fa`](https://github.com/canvas-medical/canvas-plugins/commit/4f634fa4528bbd86310f5386f6cb0e3097003c51))

* Changes for consistency ([`42282d8`](https://github.com/canvas-medical/canvas-plugins/commit/42282d8f86f689a886f7abe4e5605e635d33c698))

* Merge pull request #95 from canvas-medical/csande/KOALA-1903-allergies-data-module

SDK AllergyIntolerance model ([`87607eb`](https://github.com/canvas-medical/canvas-plugins/commit/87607eb842999f13c9ebdb04834cb552146501a5))

* A few changes for consistency ([`69d9525`](https://github.com/canvas-medical/canvas-plugins/commit/69d952546913a9ecba564afe0653132d6d38b6af))

* Updated poetry.lock ([`bc7e256`](https://github.com/canvas-medical/canvas-plugins/commit/bc7e256cad6f0b929b310c044b4ab8288b236e48))

* Merge branch 'ad/data-module-orm' into csande/KOALA-1903-allergies-data-module ([`02e8dd9`](https://github.com/canvas-medical/canvas-plugins/commit/02e8dd92ba98be617c278ab019d577e8296339db))

* Added more fields ([`e09cba1`](https://github.com/canvas-medical/canvas-plugins/commit/e09cba1f215771c433a34647d8510e005009f635))

* SDK AllergyIntolerance model ([`00795be`](https://github.com/canvas-medical/canvas-plugins/commit/00795befdfcb40b7ce857c35e0a65cb9f7e64e99))

* Merge pull request #93 from canvas-medical/feature/jw-koala-1843

Adds LabReport, LabValue and related models. ([`6f3fb21`](https://github.com/canvas-medical/canvas-plugins/commit/6f3fb2196d1258166a548bb31575e6909da06ffe))

* Removes report_data_payload_cache from LabReport model. ([`4c21d6f`](https://github.com/canvas-medical/canvas-plugins/commit/4c21d6f4383bb50eb6ec5fe8079b7339cb2ede30))

* Changes database view name for CanvasUser. ([`38aed42`](https://github.com/canvas-medical/canvas-plugins/commit/38aed42b59e0b43d6512d87c61e41f781d32208b))

* Adds system field to LabValueCoding. ([`d29a566`](https://github.com/canvas-medical/canvas-plugins/commit/d29a5665618ee0eb7188aa9ac6bfad5bec706832))

* Removes unnecessary arguments to model fields. ([`321e881`](https://github.com/canvas-medical/canvas-plugins/commit/321e881f01869d07762c823e6d4a139929e34134))

* Adds id fields to LabValue and LabReview. ([`dd35b7f`](https://github.com/canvas-medical/canvas-plugins/commit/dd35b7f276c8146e4f850699aecd48e2b604283d))

* Adds LabReport, LabValue and related models. ([`fa94895`](https://github.com/canvas-medical/canvas-plugins/commit/fa94895912db5901a1519ce2c394e43f417b7276))

* Merge pull request #91 from canvas-medical/feature/jw-valuesets-plugins

Adds value set data and filtering ([`593f0a2`](https://github.com/canvas-medical/canvas-plugins/commit/593f0a27366742a907e6c55e55f1088660c47347))

* Removes outdated comment. ([`5a9d791`](https://github.com/canvas-medical/canvas-plugins/commit/5a9d791379374fd7e3d7cbf8537386d0946df874))

* Adds pipe functionality and tests. ([`0ac4e61`](https://github.com/canvas-medical/canvas-plugins/commit/0ac4e61797f97ab0ba14e9e755cf9b460ea34dc5))

* Removes periods from ValueSet data and removes alphanum helper. ([`a4c3f6a`](https://github.com/canvas-medical/canvas-plugins/commit/a4c3f6acfd1731d700d5df7df291be0eeb0559af))

* Adds value set data and filtering. ([`9734af2`](https://github.com/canvas-medical/canvas-plugins/commit/9734af29097541fe92873e870a82a84d523f7904))

* Upgraded psycopg ([`cd9ff1d`](https://github.com/canvas-medical/canvas-plugins/commit/cd9ff1da94e50e068885cc7c6cada83dcfb644d2))

* Method name change ([`31b322b`](https://github.com/canvas-medical/canvas-plugins/commit/31b322bb5058385b1adb259b6d0117a74adc7a64))

* Add the django ORM and the first 5 models ([`0cb70a8`](https://github.com/canvas-medical/canvas-plugins/commit/0cb70a8d921c574c54f6d5d0d80af3db9203cf0e))

* Merge pull request #92 from canvas-medical/feat/koala-1984-originate-perform

feat: add Perform and Instruct Command SDK definitions ([`c58ed01`](https://github.com/canvas-medical/canvas-plugins/commit/c58ed0107d272337c44af8c8248200a9edc0ae4b))

* add events and effect to add claim condition annotation (#86) ([`3d93b4e`](https://github.com/canvas-medical/canvas-plugins/commit/3d93b4ea94845c12cd9d697b0b5967d43322eda0))

* enable all know command events including pre-search (#90) ([`d89db40`](https://github.com/canvas-medical/canvas-plugins/commit/d89db40ae87166c8828a9b3aae272b1497d78953))

* Bump cryptography from 42.0.4 to 43.0.1 (#83)

Bumps [cryptography](https://github.com/pyca/cryptography) from 42.0.4 to 43.0.1.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/42.0.4...43.0.1)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`46e9d25`](https://github.com/canvas-medical/canvas-plugins/commit/46e9d255cbba43c675929c3dcb46dfff5874b57f))

* Integration tests (#78)

This PR creates integration tests against the plugin-testing repo. ([`7964ccf`](https://github.com/canvas-medical/canvas-plugins/commit/7964ccfdce637f09116a5f7de30ca1520eb21d92))

* update version for publish ([`7e8f796`](https://github.com/canvas-medical/canvas-plugins/commit/7e8f7961dd75a06f3caf93e6e7c0190e75418bdf))


## v0.2.5 (2024-09-09)

### Unknown

* Merge pull request #82 from canvas-medical/csande/KOALA-1034-remove-dal

Remove Data Access Layer ([`9b62f64`](https://github.com/canvas-medical/canvas-plugins/commit/9b62f6400de7801c2167d55345b596b625fdaeda))

* Merge branch 'main' into csande/KOALA-1034-remove-dal ([`8cfe238`](https://github.com/canvas-medical/canvas-plugins/commit/8cfe238a2889191ee5c4222a1b415e3e955809f0))

* Merge pull request #85 from canvas-medical/feat/annotate_conditions

Add new PATIENT_CHART__CONDITIONS events and ANNOTATE_PATIENT_CHART_CONDITION_RESULTS effect ([`64b85be`](https://github.com/canvas-medical/canvas-plugins/commit/64b85be90379b80df943fe9cf61feaaea5540427))

* Add new PATIENT_CHART__CONDITIONS events and ANNOTATE_PATIENT_CHART_CONDITION_RESULTS effect ([`97d7477`](https://github.com/canvas-medical/canvas-plugins/commit/97d7477e3165cb6058c951551ccc4413f9008fe0))


## v0.2.4 (2024-09-04)

### Unknown

* Merge pull request #81 from canvas-medical/feature/jw-koala-1776

Adds GraphQL data client ([`db15859`](https://github.com/canvas-medical/canvas-plugins/commit/db158590fac3cfc90824b7388695a38f523dbb4d))


## v0.2.3 (2024-09-04)

### Unknown

* update version ([`9c2a192`](https://github.com/canvas-medical/canvas-plugins/commit/9c2a192aead981bdbfac00e2e3640f6843377e89))

* fix JWT authentication ([`55544dd`](https://github.com/canvas-medical/canvas-plugins/commit/55544dd10b142435dd6dfcb5bc5da86c731b0439))

* fix pyjwt vulnerability flagged by Snyk ([`c055588`](https://github.com/canvas-medical/canvas-plugins/commit/c0555887fb057743db1805f84c7519c1123f128f))

* rename method to hide it and fix example ENV URL ([`a959188`](https://github.com/canvas-medical/canvas-plugins/commit/a9591880a63045ab6834ba46b3ff374dadba38df))

* Fixes quotes error. ([`950f3f7`](https://github.com/canvas-medical/canvas-plugins/commit/950f3f7ed41fda425100ccfd9912e6f91c1857de))

* Update settings.py ([`b396a29`](https://github.com/canvas-medical/canvas-plugins/commit/b396a29ae9077bb751f1eb1d60a7348f3641fc14))


## v0.2.2 (2024-09-03)

### Unknown

* update example and use default since it won't change ([`afbf9be`](https://github.com/canvas-medical/canvas-plugins/commit/afbf9bebb6984190141406d2f44d61ce0b910a97))

* remove unused code ([`2a223ac`](https://github.com/canvas-medical/canvas-plugins/commit/2a223ac733784b63ba18a305916ce2b9c3996e2a))


## v0.2.0 (2024-09-03)

### Unknown

* fix import ([`a2e0757`](https://github.com/canvas-medical/canvas-plugins/commit/a2e0757afe2159fe0f6564b9ae19f3082dfeb065))

* bump version ([`0362796`](https://github.com/canvas-medical/canvas-plugins/commit/03627962d7d7998049f0ea42391d385262cd9edd))

* fix self-referential import ([`f39ff71`](https://github.com/canvas-medical/canvas-plugins/commit/f39ff71af5a0e218a89c51a8fed3a889771d513e))

* remove unused GRAPHQL_AUTH_KEY ([`78cb46c`](https://github.com/canvas-medical/canvas-plugins/commit/78cb46c4be6b7b1e704e750b8f7b087d9473e1c2))

* add WIP for per-plugin GraphQL JWT auth ([`c71338e`](https://github.com/canvas-medical/canvas-plugins/commit/c71338e01b1dbdd626d480cdc6e0e430b95572df))

* Adds run_gql_query method that uses the gql client. ([`4f264a0`](https://github.com/canvas-medical/canvas-plugins/commit/4f264a0fe878a5ac1bda1290988b9c16ee49e28b))

* Removes DAL_ prefix from variable names. ([`2837aa4`](https://github.com/canvas-medical/canvas-plugins/commit/2837aa4351461a458ba373eb19af8e12363c55da))

* Adds to docstring. ([`c9207a2`](https://github.com/canvas-medical/canvas-plugins/commit/c9207a29dee628b91908db2f5576b534960fa93a))

* Adds GQL_CLIENT to BaseHandler. ([`b02470f`](https://github.com/canvas-medical/canvas-plugins/commit/b02470f3b676667c70b6649948206b3fc1324fa1))

* Addresses items from code review. ([`9234061`](https://github.com/canvas-medical/canvas-plugins/commit/923406148d678b51f98c8d4620b9845a76b434f5))

* Changes back env variable for original DAL. ([`904b0d1`](https://github.com/canvas-medical/canvas-plugins/commit/904b0d17302ed8737b6d6a3a8366652b17a16b83))

* Adds GraphQL data client. ([`3759f66`](https://github.com/canvas-medical/canvas-plugins/commit/3759f663f8f9a1e7b09e5bc353a1316f6dda9b6a))

* Remove Data Access Layer ([`b7f57d8`](https://github.com/canvas-medical/canvas-plugins/commit/b7f57d8c3196319df20307fa59c4e2f536a8e199))

* Merge pull request #80 from canvas-medical/csande/add-missing-protobuf-dependency

Added protobuf as a dependency ([`ccdcf2e`](https://github.com/canvas-medical/canvas-plugins/commit/ccdcf2eed185764a9a98473017ce4ba091a3bae0))

* Regenerated lock file ([`80126a1`](https://github.com/canvas-medical/canvas-plugins/commit/80126a19a42e75fd4a6b8781d5baa513efd2288e))

* Downgraded protobuf to the version currently in the lock file ([`3f6114d`](https://github.com/canvas-medical/canvas-plugins/commit/3f6114dfa3f685a832e8352595155ef797cb8b11))

* Added protobuf as a dependency ([`40d069c`](https://github.com/canvas-medical/canvas-plugins/commit/40d069cff5c03e7e0f76ac64025ce448ef83202e))

* Merge pull request #79 from canvas-medical/csande/change-dal-target-env-var-name

Renamed DAL target environment variable ([`0bef4d4`](https://github.com/canvas-medical/canvas-plugins/commit/0bef4d4362367b3bbc37bf6174cd2e840ab23287))

* Renamed DAL target environment variable ([`7e87b3e`](https://github.com/canvas-medical/canvas-plugins/commit/7e87b3eea1bcf7047b4d0aef72c3ff1b761a5a81))


## v0.1.15 (2024-07-25)

### Unknown

* Bump the package version ([`46b5c87`](https://github.com/canvas-medical/canvas-plugins/commit/46b5c87ed2953cc5f53814fd8246851d77b54753))

* for enable/disable check for status ok to give success message ([`87a43a1`](https://github.com/canvas-medical/canvas-plugins/commit/87a43a188db6fc522d5013184f8c2838467f09c5))

* Bump certifi from 2024.2.2 to 2024.7.4 (#65)

Bumps [certifi](https://github.com/certifi/python-certifi) from 2024.2.2 to 2024.7.4.
- [Commits](https://github.com/certifi/python-certifi/compare/2024.02.02...2024.07.04)

---
updated-dependencies:
- dependency-name: certifi
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`3b6c59c`](https://github.com/canvas-medical/canvas-plugins/commit/3b6c59cdc92e7c56299649ea0de748651c3d96a6))

* Bump urllib3 from 2.2.1 to 2.2.2 (#59)

Bumps [urllib3](https://github.com/urllib3/urllib3) from 2.2.1 to 2.2.2.
- [Release notes](https://github.com/urllib3/urllib3/releases)
- [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst)
- [Commits](https://github.com/urllib3/urllib3/compare/2.2.1...2.2.2)

---
updated-dependencies:
- dependency-name: urllib3
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`12de79e`](https://github.com/canvas-medical/canvas-plugins/commit/12de79e5ecaf9589bae5d075cab31c9442d6867e))

* Bump requests from 2.31.0 to 2.32.2 (#56)

Bumps [requests](https://github.com/psf/requests) from 2.31.0 to 2.32.2.
- [Release notes](https://github.com/psf/requests/releases)
- [Changelog](https://github.com/psf/requests/blob/main/HISTORY.md)
- [Commits](https://github.com/psf/requests/compare/v2.31.0...v2.32.2)

---
updated-dependencies:
- dependency-name: requests
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`0be07b6`](https://github.com/canvas-medical/canvas-plugins/commit/0be07b651cb5f8730a412e30913923af9dcf5d61))

* Bump jinja2 from 3.1.3 to 3.1.4 (#35)

Bumps [jinja2](https://github.com/pallets/jinja) from 3.1.3 to 3.1.4.
- [Release notes](https://github.com/pallets/jinja/releases)
- [Changelog](https://github.com/pallets/jinja/blob/main/CHANGES.rst)
- [Commits](https://github.com/pallets/jinja/compare/3.1.3...3.1.4)

---
updated-dependencies:
- dependency-name: jinja2
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`9aab6c7`](https://github.com/canvas-medical/canvas-plugins/commit/9aab6c767b730adfbb08c77eb0e8f1438185eaf5))

* Bump zipp from 3.17.0 to 3.19.1 (#66)

Bumps [zipp](https://github.com/jaraco/zipp) from 3.17.0 to 3.19.1.
- [Release notes](https://github.com/jaraco/zipp/releases)
- [Changelog](https://github.com/jaraco/zipp/blob/main/NEWS.rst)
- [Commits](https://github.com/jaraco/zipp/compare/v3.17.0...v3.19.1)

---
updated-dependencies:
- dependency-name: zipp
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`0cc8c1e`](https://github.com/canvas-medical/canvas-plugins/commit/0cc8c1e0dd70765e1bb62b7d546c4a825f840c4b))

* Bump setuptools from 69.1.0 to 70.0.0 (#71)

Bumps [setuptools](https://github.com/pypa/setuptools) from 69.1.0 to 70.0.0.
- [Release notes](https://github.com/pypa/setuptools/releases)
- [Changelog](https://github.com/pypa/setuptools/blob/main/NEWS.rst)
- [Commits](https://github.com/pypa/setuptools/compare/v69.1.0...v70.0.0)

---
updated-dependencies:
- dependency-name: setuptools
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`a5ee78d`](https://github.com/canvas-medical/canvas-plugins/commit/a5ee78de5928e607bba62f05788069c952299bf0))

* Merge pull request #72 from canvas-medical/csande/KOALA-1546-dal-grpc-client

Data Access Layer ([`c736e57`](https://github.com/canvas-medical/canvas-plugins/commit/c736e57d3f1c0aba934ca8436bb1f82298a15f53))

* Renamed exceptions ([`0a848f7`](https://github.com/canvas-medical/canvas-plugins/commit/0a848f79d08cb1d04e335c27b74d6dd531e82b15))

* Added try-except around getting error details ([`ebff547`](https://github.com/canvas-medical/canvas-plugins/commit/ebff547a7599ccfd684482ace9247133db69ed07))

* Added another except clause ([`c642b9f`](https://github.com/canvas-medical/canvas-plugins/commit/c642b9fedd6a007f5371daf02453a6cdb812f547))

* Renamed variable ([`bbfac19`](https://github.com/canvas-medical/canvas-plugins/commit/bbfac1920e64328493bf2384527e12db028024c1))

* Formatting and mypy ([`0a8c7f7`](https://github.com/canvas-medical/canvas-plugins/commit/0a8c7f7cf97a70cf826aefa421f63cc7ed8375f3))

* Improve handling of optional fields; parse birth date correctly ([`f0534c6`](https://github.com/canvas-medical/canvas-plugins/commit/f0534c60bd62e353c3567fed84f78e57d1ad78ab))

* Merge branch 'main' into csande/KOALA-1546-dal-grpc-client ([`5d76b56`](https://github.com/canvas-medical/canvas-plugins/commit/5d76b56e550d9a3bb45e948504340ed067b18d32))


## v0.1.14 (2024-07-17)

### Unknown

* Merge pull request #76 from canvas-medical/ad/version-bump-to-0.1.14

bump the package version to 0.1.14 ([`04f3241`](https://github.com/canvas-medical/canvas-plugins/commit/04f3241ee5ef79b51aa13b5e68e67e149214446b))

* bump the package version to 0.1.14 ([`4c8161d`](https://github.com/canvas-medical/canvas-plugins/commit/4c8161de0e59f8ffc2568862fea6ffea632505f9))

* Merge pull request #75 from canvas-medical/ad/cron-events

Add support for periodic tasks with cron schedules ([`b9973da`](https://github.com/canvas-medical/canvas-plugins/commit/b9973da0af74f7e6793336050057cf09745e9aa2))

* Bump the version ([`5fe43af`](https://github.com/canvas-medical/canvas-plugins/commit/5fe43afac7767574ccdc9a256f5c474e043f34d7))

* Do not set a default schedule, force the plugin author to define one. ([`907db10`](https://github.com/canvas-medical/canvas-plugins/commit/907db1053b2d2aa07a4b639a5c6603ccff4dc68d))

* Add support for periodic tasks with cron schedules ([`3f9f7c0`](https://github.com/canvas-medical/canvas-plugins/commit/3f9f7c056784e130522bd4022c98f7b4fc419f45))

* Merge pull request #64 from canvas-medical/feature/jw-koala-1579-canvas-plugins

Task Creation, Update and Comment Additions ([`df815ae`](https://github.com/canvas-medical/canvas-plugins/commit/df815aeec042e373d32dbca9ce855849ec31d4cb))

* Fixes required fields logic. ([`83b3881`](https://github.com/canvas-medical/canvas-plugins/commit/83b3881ef3d37a6ad5ae756e9fb68b5383e4e2d2))

* Removes Optional annotations. ([`09aadf1`](https://github.com/canvas-medical/canvas-plugins/commit/09aadf101950d2ddda4a7a4d1d88a89f410bb5ef))

* Adds plugin task creation, update and comment addition functionality with validation. ([`d74423b`](https://github.com/canvas-medical/canvas-plugins/commit/d74423b7a0f7db7399f9fd0ca8e01740b94a73d7))

* Merge pull request #74 from canvas-medical/csande/ide-fixes

IDE fixes ([`04df953`](https://github.com/canvas-medical/canvas-plugins/commit/04df9533d72bf4b712bf3e2968a0ef95cbdacc4e))

* Added imports for commented-out code in the protocol templae ([`1b2dd1c`](https://github.com/canvas-medical/canvas-plugins/commit/1b2dd1cc990f8a51ca24419bbb1477cfa439aff8))

* added some additional directories in the pyproject file to be included when the package is built ([`730ebd1`](https://github.com/canvas-medical/canvas-plugins/commit/730ebd10047ba7d042f456ff4b08c248f69fe4d7))

* Merge pull request #69 from canvas-medical/ad/prepend-hostname-to-log

Prepend the hostname to log lines if the hostname is defined in the env ([`5947d84`](https://github.com/canvas-medical/canvas-plugins/commit/5947d84d5e216532446422cc179b381c8e08ba7a))

* Change a class name to be more descriptive ([`acfe982`](https://github.com/canvas-medical/canvas-plugins/commit/acfe9826c299f7f0ef8bd63a38c83930901e0db8))

* Obfuscate a testing secret from logs ([`274a10e`](https://github.com/canvas-medical/canvas-plugins/commit/274a10e0c77fa1898f37b847feff2f44653b2644))

* Prepend the hostname to log lines if the hostname is defined in the env ([`0e3cb01`](https://github.com/canvas-medical/canvas-plugins/commit/0e3cb019ff5f67277a9e548a640d695a78616529))

* Merge pull request #73 from canvas-medical/ad/prevent-boot-looping

Prevent bootlooping due to a failed plugin load. ([`978eae8`](https://github.com/canvas-medical/canvas-plugins/commit/978eae8528b93546a25987b8c1e427204db5d2a9))

* Prevent bootlooping due to a failed plugin load.

We already skip plugins that fail to load due to an ImportError, this
change increases the types of errors that would skip a plugin
considerably. It is extremely important to prevent the process from
crashing on load, as circus will immediately attempt to resurrect it,
causing a bootloop. ([`aa3379b`](https://github.com/canvas-medical/canvas-plugins/commit/aa3379bb785b0659341666ccd89ffbd721ffac16))

* Validate command classes on demand, with specific validation for each type of effect (#68) ([`264f8b2`](https://github.com/canvas-medical/canvas-plugins/commit/264f8b231eb56c13162c76a53c18922974bc2b8b))

* Create enable and disable cli methods (#70) ([`68170c8`](https://github.com/canvas-medical/canvas-plugins/commit/68170c8aaad59a833f4249af85d9b922317fc16a))

* Added DAL client and Patient get classmethod ([`2cad95c`](https://github.com/canvas-medical/canvas-plugins/commit/2cad95ccd341a9dca751a6c98eb0b61f69d8016c))

* Added gRPC genereated code for the Data Access Layer ([`206cda5`](https://github.com/canvas-medical/canvas-plugins/commit/206cda55642b52866b410b8285d64887e6b33be2))


## v0.1.13 (2024-07-03)

### Unknown

* Merge pull request #63 from canvas-medical/ad/add-many-more-command-events

Add many command origination events. ([`2a3ecb5`](https://github.com/canvas-medical/canvas-plugins/commit/2a3ecb5fb91d53e5d2e4691f40365b4bb5078f10))

* Fix tests ([`278780c`](https://github.com/canvas-medical/canvas-plugins/commit/278780cda26cf065d005179d5b2595c9ef321d56))

* Ignore this attribute for now ([`ad9dc2c`](https://github.com/canvas-medical/canvas-plugins/commit/ad9dc2c4e3d6f09493fba26d0a160048c226b28e))

* Some type changes for the prescribe command. ([`4455eb1`](https://github.com/canvas-medical/canvas-plugins/commit/4455eb1c2774463ce097baed51d28a56e3df938a))

* Revert some changes I had made ([`14cb669`](https://github.com/canvas-medical/canvas-plugins/commit/14cb66982ea4692e2328849486fc11a3ec77348d))

* Move some of the attribute manipulation logic to the effect interpreter side. ([`9f3de1b`](https://github.com/canvas-medical/canvas-plugins/commit/9f3de1bd2c0fdcbecbe46b4e3d3bbbb0af3d1d89))

* Update fixture event attribute ([`e32a590`](https://github.com/canvas-medical/canvas-plugins/commit/e32a590f217273046e195eb74167ec19fa0da75d))

* WIP: Fix diagnosis command date display issue and start on the diagnosis coding issue ([`237bfe5`](https://github.com/canvas-medical/canvas-plugins/commit/237bfe58e78e8355951fe57f5e8bcd12f2b7be1d))

* Fix what looks like a copy/paste error in goal. ([`5546b48`](https://github.com/canvas-medical/canvas-plugins/commit/5546b4896d1d4f355f42920625d7d49dd220da51))

* Use note uuid instead of note id. Not sure I like the attribute rename, but we must use the uuid over the int id. ([`6db8146`](https://github.com/canvas-medical/canvas-plugins/commit/6db81467da40839e5d581929183a9073d6a6daf9))

* Add many more command events. This won't have an effect until we write the interpreters, however. ([`fe4991e`](https://github.com/canvas-medical/canvas-plugins/commit/fe4991e03f69b619f8a13dd61264e2ba1540a0d2))

* Merge pull request #61 from canvas-medical/michela/koala-1465-banner-alerts

Update banner alert effects ([`25c961a`](https://github.com/canvas-medical/canvas-plugins/commit/25c961a6a99d0cb1d7d091b09140b2f67507bcb5))

* Developer ergonomics changes ([`d4b8efe`](https://github.com/canvas-medical/canvas-plugins/commit/d4b8efe173b25f53d6d65e78c603f25c4fd7d151))

* delete customplugin and regenerate effects ([`fc327cd`](https://github.com/canvas-medical/canvas-plugins/commit/fc327cdce8223f3dfc7f9b27f85478a79c321ce7))

* fix precommit and init and generated/ ([`63fc4e8`](https://github.com/canvas-medical/canvas-plugins/commit/63fc4e86c7cb92e1ad1effa2b2c005e8f19bd300))

* update banner alert effects ([`b09d627`](https://github.com/canvas-medical/canvas-plugins/commit/b09d627da7621ccb8db76c10d8ed8e1960a6bf40))

* Merge pull request #60 from canvas-medical/feature/jw-koala-1516

Adds timing metrics for Protocol compute and Event response ([`9c7d6ec`](https://github.com/canvas-medical/canvas-plugins/commit/9c7d6ec9009399b6f1ed9a65e062616eb03d7d70))

* Removes unused CUSTOMER_IDENTIFIER variable. ([`7825c13`](https://github.com/canvas-medical/canvas-plugins/commit/7825c1318b535f73d04b3186c434098793f06f3b))

* Fixes formatting issues. ([`9ade7b1`](https://github.com/canvas-medical/canvas-plugins/commit/9ade7b13d092ea06cddb996516005b2101673f56))

* Adds formatting to send to grafana. ([`7989e25`](https://github.com/canvas-medical/canvas-plugins/commit/7989e253e7d3fb0e5966244ad485ada8c90f43dd))

* Removes customer arg and renames protocol to plugin. ([`30cba78`](https://github.com/canvas-medical/canvas-plugins/commit/30cba7824f011a17902e0ea11866e322fd218aaf))

* Adds log statement for testing. ([`f4a753e`](https://github.com/canvas-medical/canvas-plugins/commit/f4a753ed71e3da4f9be397d30c3be0f559fbc913))

* Changes metrics naming. ([`7ffa846`](https://github.com/canvas-medical/canvas-plugins/commit/7ffa8463e0fda12932bf4c5b36a9975750280b9c))

* Adds timing stats to protocol computations and event responses. ([`a487ca7`](https://github.com/canvas-medical/canvas-plugins/commit/a487ca778cfa0e0bcc0eeb53be85fd6142331f62))

* Merge pull request #62 from canvas-medical/ad/rename_generated_module

Rename generated module to canvas_generated ([`d8a83c8`](https://github.com/canvas-medical/canvas-plugins/commit/d8a83c8009bdb3ccc100882b8ab39e8b3bf95c20))

* Rename generated module to canvas_generated to avoid conflicts with other modules people may have installed ([`54ff62a`](https://github.com/canvas-medical/canvas-plugins/commit/54ff62adc4070db71e44d6043bf708b20e3cf5db))


## v0.1.12 (2024-06-17)

### Unknown

* bump version for cli publish ([`b60a40d`](https://github.com/canvas-medical/canvas-plugins/commit/b60a40d1ea997218f664a459e17d05a7ba9b174e))

* Merge pull request #58 from canvas-medical/ad/emit-events-via-cli

Emit events via CLI ([`c48ddfd`](https://github.com/canvas-medical/canvas-plugins/commit/c48ddfd5bdc9d41acdc744f84766fe0cbd9205b3))

* Incorporate PR feedback ([`42d3809`](https://github.com/canvas-medical/canvas-plugins/commit/42d38096a90a24723a006e1b046eb569b93253f0))

* Add CLI command to simulate an event from a fixture file ([`8c17061`](https://github.com/canvas-medical/canvas-plugins/commit/8c17061110f0589a1266ff4d516245e5f8918e17))

* Add some fixture files for events ([`639145e`](https://github.com/canvas-medical/canvas-plugins/commit/639145eab489a8c7afaa97c0ed3939206fc2dce5))

* use the CUSTOMER_IDENTIFIER ([`536a08c`](https://github.com/canvas-medical/canvas-plugins/commit/536a08cd7f90c55fce182e17c2f218dfe964b063))


## v0.1.11 (2024-06-12)

### Unknown

* Merge pull request #57 from canvas-medical/jw-fix-protobuf-msgs

Regenerates protobuf files. ([`e2a4afc`](https://github.com/canvas-medical/canvas-plugins/commit/e2a4afcc220af67d90dfa61a0d91f4f4475ba218))

* Regenerates protobuf files. ([`944562e`](https://github.com/canvas-medical/canvas-plugins/commit/944562e780b365a29a9cb6fbaaf367e7b765a9fc))

* Add post search events for refactored commands (#53) ([`3083d5c`](https://github.com/canvas-medical/canvas-plugins/commit/3083d5cf9262397b604b3a4e8513521f9a99a522))


## v0.1.10 (2024-05-31)

### Unknown

* Merge pull request #55 from canvas-medical/ad/fixes-from-live-demo

Fixes from feedback during live demo ([`bcd247b`](https://github.com/canvas-medical/canvas-plugins/commit/bcd247bc2a2bc7ed7135cd5d40f61bb39c944c24))

* Bump version number ([`3c4aa7e`](https://github.com/canvas-medical/canvas-plugins/commit/3c4aa7eca94cecd53cb3c9af632f8ced552e0edc))

* Usability improvements to the Canvas CLI output. ([`77d38f1`](https://github.com/canvas-medical/canvas-plugins/commit/77d38f1ea3fee2e02ef098f0ae3bcd2aa44a253d))

* simplify the CLI ([`e77c1ff`](https://github.com/canvas-medical/canvas-plugins/commit/e77c1ff5ef5b6f87bef8a0adaeb4623f188671b0))

* formatting changes for logger ([`fca3ba1`](https://github.com/canvas-medical/canvas-plugins/commit/fca3ba104a30dc8b17395a2ea736f6aa8cf88e89))

* handle exceptions during plug load/reload ([`cd467d0`](https://github.com/canvas-medical/canvas-plugins/commit/cd467d0a2bdd38dafb4786f412ab1d42cb3ef3c3))

* add more canvas_sdk modules ([`a530614`](https://github.com/canvas-medical/canvas-plugins/commit/a5306140fdbb9e504e9abefab928fd2d55cc3d7b))

* note that we need to use CUSTOMER_IDENTIFIER in the PLUGINS_PUBSUB_CHANNEL ([`9e6246a`](https://github.com/canvas-medical/canvas-plugins/commit/9e6246a50bbb1831d6c86d7904d44047f3b69071))

* add canvas_sdk.utils to allowed libraries ([`d760363`](https://github.com/canvas-medical/canvas-plugins/commit/d76036330e2d1470ebc08cfa5d86b40a21a0b84a))

* Merge pull request #51 from canvas-medical/csande/protocol-executor

Run Protocol compute method in a threadpool to avoid blocking the main event loop ([`6ebf1da`](https://github.com/canvas-medical/canvas-plugins/commit/6ebf1daf1ec1683ee8f2f985b0614f76b0b10d34))

* Run Protocol compute method in a threadpool to avoid blocking the main event loop ([`aa320f4`](https://github.com/canvas-medical/canvas-plugins/commit/aa320f4e12800be7d969a746569e20f3f8276767))


## v0.1.9 (2024-05-31)

### Unknown

* Merge pull request #54 from canvas-medical/ad/fix-protocol-initialization-bug

Fix protocol initialization issues ([`5861e65`](https://github.com/canvas-medical/canvas-plugins/commit/5861e652fc1a2b5a6424a79b9f6aed6e553fe40b))

* Set target on protocol initialization and be permissive if there is no provided context. ([`ebed450`](https://github.com/canvas-medical/canvas-plugins/commit/ebed45020a129fea07ce1f89491853783dcf2c94))

* add back .gitkeep ([`a7bf010`](https://github.com/canvas-medical/canvas-plugins/commit/a7bf0103a49152637c66efb6cbbfacfd0c626bbc))


## v0.1.7 (2024-05-17)

### Unknown

* 0.1.7 ([`a9efda5`](https://github.com/canvas-medical/canvas-plugins/commit/a9efda5bd6c817e585f5634ee963a843eaed195b))

* add HUP handler for plugin_runner ([`0febd21`](https://github.com/canvas-medical/canvas-plugins/commit/0febd21f6a4887df84235162ced41601229d529d))

* Merge pull request #49 from canvas-medical/jw-remove-add-plan-from-template

Removes ADD_PLAN_COMMAND from examples. ([`f1fe305`](https://github.com/canvas-medical/canvas-plugins/commit/f1fe305e5723afd6c9456f257444f0f7909ef914))

* Removes ADD_PLAN_COMMAND from examples. ([`696bdca`](https://github.com/canvas-medical/canvas-plugins/commit/696bdcad5e0ba67279a5379026356676d6fb3844))

* add plugin synchronization ([`dc9e4a9`](https://github.com/canvas-medical/canvas-plugins/commit/dc9e4a9ac53011a8e54e4df6db6ec293e86f82a8))

* Merge pull request #48 from canvas-medical/jw-log-fix

Fixes log statement. ([`dfae13d`](https://github.com/canvas-medical/canvas-plugins/commit/dfae13de8833eed0fa08587dea50f5a3f625f73a))


## v0.0.7 (2024-05-16)

### Unknown

* Fixes log statement. ([`3d1f8b3`](https://github.com/canvas-medical/canvas-plugins/commit/3d1f8b30d3458ae56fc3e80d04fcba40f07105d9))

* make name match class on test plugin ([`0bcd448`](https://github.com/canvas-medical/canvas-plugins/commit/0bcd44818a20d464692206e58ba7917308725488))

* Merge pull request #47 from canvas-medical/csande/update-gitignore

Updated .gitignore ([`df686dc`](https://github.com/canvas-medical/canvas-plugins/commit/df686dcd7a229c9abc92ad67ff657af330b8a88e))

* Updated .gitignore ([`cb566e2`](https://github.com/canvas-medical/canvas-plugins/commit/cb566e278433050f0f4853c5eb23ecd855d28f87))


## v0.0.6 (2024-05-14)

### Unknown

* update version ([`44849d0`](https://github.com/canvas-medical/canvas-plugins/commit/44849d076945ff09906f96f33e11a70b0188577b))

* Merge pull request #45 from canvas-medical/jw-log-changes

Changes log statements. ([`0ebaf51`](https://github.com/canvas-medical/canvas-plugins/commit/0ebaf51a0a17e37c97c72ed6209c9b5747028077))

* Changes log statements. ([`b1043ff`](https://github.com/canvas-medical/canvas-plugins/commit/b1043ff0c8b1bcfa61b21a12b30090b324689292))

* Merge pull request #46 from canvas-medical/jw-cookiecutter-change

Changes cookiecutter class to use colon. ([`eff7661`](https://github.com/canvas-medical/canvas-plugins/commit/eff7661e3bf451d1db8e09b9d52cb13767b45a91))

* Changes cookiecutter class to use colon. ([`0e8f1ff`](https://github.com/canvas-medical/canvas-plugins/commit/0e8f1ffbe3666d2715aff363c656c4e089cfa377))

* update version ([`1bbbbbb`](https://github.com/canvas-medical/canvas-plugins/commit/1bbbbbb6bf99b0e09b476658f98d11e07fe5ef24))

* allow specifying subdomain or URL, fix possibly null hostname ([`2e969ee`](https://github.com/canvas-medical/canvas-plugins/commit/2e969eee5905b123f1200cbb7f57f99a5e64c14c))

* Merge pull request #42 from canvas-medical/michela/auth-scope

Add plugin scope to oauth token request. and tests ([`bec6c7c`](https://github.com/canvas-medical/canvas-plugins/commit/bec6c7c11cb6a87cb0caa1321731e6766065db5b))

* add scope and tests ([`f0243bb`](https://github.com/canvas-medical/canvas-plugins/commit/f0243bbb1739d716d9a9419caf97b68f7dbe67c7))

* Merge pull request #43 from canvas-medical/ad/plugin-init-updates

Simplify plugin init ([`8e8b635`](https://github.com/canvas-medical/canvas-plugins/commit/8e8b63545469e2ace3ba52bff4b8e0a7aeb2bf13))

* Simplify Plugin Template

- Remove unused pyproject.toml
- Ask a single question when generating plugin
- Remove directories that cannot be used now
  but are anticipated for future use
- Correct the directory structure (was nested a
  level too deeply)
- Include a commented protocol to help orient the
  developer ([`4df7583`](https://github.com/canvas-medical/canvas-plugins/commit/4df7583ca3985705764e53913073af48dfd5f66f))

* Add example secrets declaration in test plugin CANVAS_MANIFEST.json ([`c7f3a5e`](https://github.com/canvas-medical/canvas-plugins/commit/c7f3a5eb4b1abd34f581bf4bb6944474af480f13))


## v0.0.5 (2024-05-13)

### Unknown

* Merge pull request #41 from canvas-medical/ad/add-back-deleted-and-important-directory

This directory is really important and needs to be here. ([`b2b79a7`](https://github.com/canvas-medical/canvas-plugins/commit/b2b79a78a3d2ec5d108e69d25a50029602628255))

* This directory is really important and needs to be here. ([`744fa06`](https://github.com/canvas-medical/canvas-plugins/commit/744fa0635f6cf3624acea2d2ecb72e32860df4ad))


## v0.0.4 (2024-05-13)

### Unknown

* Merge pull request #40 from canvas-medical/michela/auth-documentation-and-http-cleanup

Clean up some http code+tests, and add auth setup documentation ([`684ea0f`](https://github.com/canvas-medical/canvas-plugins/commit/684ea0f8ff83c10245363dcc45b442dd00621023))

* clean up some http code and tests, and also add help text and documentation for auth setup ([`6b69a61`](https://github.com/canvas-medical/canvas-plugins/commit/6b69a61c8fa9d86597b00a73757ac4a31a9bdf78))

* Merge pull request #37 from canvas-medical/jw-koala-1336

Plugin Runner Log Streaming ([`ee1b9c3`](https://github.com/canvas-medical/canvas-plugins/commit/ee1b9c33695d71b8bc4e54e893a44f8abeb998b0))

* Changes pubsub condition to use REDIS_ENDPOINT and adds more explicit traceback method. ([`14f2622`](https://github.com/canvas-medical/canvas-plugins/commit/14f2622852841863abb0af6606b8610a554ec944))

* Adds traceback to exceptions in logging. ([`687594a`](https://github.com/canvas-medical/canvas-plugins/commit/687594a673742632530fa09d76854be313a2f8a6))

* Moves log import. ([`d841e96`](https://github.com/canvas-medical/canvas-plugins/commit/d841e965e71ad069f8d7ee5fff910889569bee84))

* Fixes typo in channel suffix. ([`99b5493`](https://github.com/canvas-medical/canvas-plugins/commit/99b549332260fca3c53b3f341abbb8e5e0fc65e1))

* Removes default development ENV variable. ([`ea4ecaf`](https://github.com/canvas-medical/canvas-plugins/commit/ea4ecaff01a089c504ad3553de9d0d3f4a993575))

* Removes print statement. ([`ed14621`](https://github.com/canvas-medical/canvas-plugins/commit/ed146216c9023a9393577efb0954a9be85a22b36))

* Moves print statement for testing. ([`9bc792e`](https://github.com/canvas-medical/canvas-plugins/commit/9bc792e2ef3fd136ba0e75aadc34bbbf783ba221))

* Adds temporary print statements for testing with home-app. ([`5924a75`](https://github.com/canvas-medical/canvas-plugins/commit/5924a75f813fc49c20f54ebefbb5acba9c202fbe))

* Additions to log streaming functionality. ([`f1784d9`](https://github.com/canvas-medical/canvas-plugins/commit/f1784d9771494c2b376a3d574bf25b5eddac37de))

* Removes commented unused import. ([`798b67e`](https://github.com/canvas-medical/canvas-plugins/commit/798b67e6243ae6060e991a5af0c178866d09577c))

* Initial additions for log streaming. ([`009e300`](https://github.com/canvas-medical/canvas-plugins/commit/009e300a77921ffe546927de8092a6739db8c007))

* Merge pull request #39 from canvas-medical/ad/load-plugin-secrets-if-present

Load plugin secrets if present ([`1aa11a4`](https://github.com/canvas-medical/canvas-plugins/commit/1aa11a4afb46355b6e7d073420ee45fb180063e9))

* Fix mutable-default-arguments bug ([`42bf7f0`](https://github.com/canvas-medical/canvas-plugins/commit/42bf7f09f96a3f4c58aa60fa6cb1aee885f8459c))

* Add back a test plugin, but in a location it won't be loaded by accident. ([`26d8326`](https://github.com/canvas-medical/canvas-plugins/commit/26d832620134b0b8688cf29e534fda15b082777b))

* Look for a secrets json file, load it if it exists, and initialize plugins with applicable secrets. ([`fe38865`](https://github.com/canvas-medical/canvas-plugins/commit/fe388657accc952315202b6ea618df224433f656))

* Now that we can install plugins, we don't need to ship these with the runner. Also, since we're getting close to launch, we want to make sure these test plugins don't actually end up running somewhere. ([`c685920`](https://github.com/canvas-medical/canvas-plugins/commit/c685920e2a2783b3ec368d2bb52603c68f604dc0))

* Build out http helper class (#36)

An abstraction on the requests library ([`b4bc617`](https://github.com/canvas-medical/canvas-plugins/commit/b4bc6174275872043e6dbd4ec8c7642a294747ad))

* Merge pull request #38 from canvas-medical/ad/plugin-secrets

Plugins can declare secrets in the manifest ([`035cc17`](https://github.com/canvas-medical/canvas-plugins/commit/035cc17aecc0eccda07a05c9654e7dc9608219d8))

* Allow the cli to work on a local canvas install ([`41636aa`](https://github.com/canvas-medical/canvas-plugins/commit/41636aab096b250dc17994cb4441115d5f8acafc))

* The manifest allows, but does not require, declared secrets. ([`595230c`](https://github.com/canvas-medical/canvas-plugins/commit/595230c0f26bf22e7a7d79edce118cdb8ab739d2))

* Simplify the CLI (#34) ([`76e2643`](https://github.com/canvas-medical/canvas-plugins/commit/76e2643a0e5f8e3904aa39b7b1833c97bcd0fd5a))

* Merge pull request #29 from canvas-medical/feature/jw-koala-1276

Adds command-specific event types. ([`7d1c006`](https://github.com/canvas-medical/canvas-plugins/commit/7d1c0065aa08ee7bb91a4eba8785556a1453bb49))

* Moves UNKNOWN above comment. ([`7ccb021`](https://github.com/canvas-medical/canvas-plugins/commit/7ccb0219a8a2e92eeebc5869fd594df387f66112))

* Removes debug code. ([`9cba832`](https://github.com/canvas-medical/canvas-plugins/commit/9cba8325e34eea3f8d24b8ef7b006951b3356f8c))

* Removes some message types after functionality review. ([`aa81b3d`](https://github.com/canvas-medical/canvas-plugins/commit/aa81b3d61a535ca7e531ffddf56b0749361080e5))

* Updated event types. ([`fef77cf`](https://github.com/canvas-medical/canvas-plugins/commit/fef77cf03b755f7894dae9596d33ed6e13072f9e))

* Adds back general command events. ([`d145bea`](https://github.com/canvas-medical/canvas-plugins/commit/d145bea867ff0af9c583ce422a016ec830345614))

* Removes generic and adds command-specific event types. ([`9ebe9bd`](https://github.com/canvas-medical/canvas-plugins/commit/9ebe9bd48cc8a1bda7820660a51c9946d08f97bf))

* Merge pull request #33 from canvas-medical/jw-protocol-init

Moves __init__ to BaseProtocol class ([`a9823c9`](https://github.com/canvas-medical/canvas-plugins/commit/a9823c96ddb5802c54ceda45556542851d5d48d4))

* Moves __init__ to BaseProtocol class. ([`d449424`](https://github.com/canvas-medical/canvas-plugins/commit/d44942451093030ae2a7febc8142a7890cef7028))

* add sandboxing for plugin/protocol code ([`155c61b`](https://github.com/canvas-medical/canvas-plugins/commit/155c61b8aa03894d03d9efab8dd040470fc891b4))

* add missing required manifest attributes ([`1aab737`](https://github.com/canvas-medical/canvas-plugins/commit/1aab7371c9b58188aa128e779f44844f1ed73c1b))

* show help by default and fix issues with plugin installation ([`0d664e5`](https://github.com/canvas-medical/canvas-plugins/commit/0d664e5e53329daeb4ca774d7e7c65d11b792977))

* Update manifest file schema (#23)

This PR updates the manifest file schema to make tags a part of the schema itself. It also makes the tag check a warning rather than an error. ([`67390c4`](https://github.com/canvas-medical/canvas-plugins/commit/67390c4083460c7d708ef6fd5f260c8c777ee0bc))

* Change auth from api-key to client credentials (#30) ([`01c4689`](https://github.com/canvas-medical/canvas-plugins/commit/01c46892e5693a3263242ce0613c1e0bf5ac2eb6))

* Bump idna from 3.6 to 3.7 (#31)

Bumps [idna](https://github.com/kjd/idna) from 3.6 to 3.7.
- [Release notes](https://github.com/kjd/idna/releases)
- [Changelog](https://github.com/kjd/idna/blob/master/HISTORY.rst)
- [Commits](https://github.com/kjd/idna/compare/v3.6...v3.7)

---
updated-dependencies:
- dependency-name: idna
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`df0333b`](https://github.com/canvas-medical/canvas-plugins/commit/df0333b8461692b21fdcc2da2052aa44f2a71987))

* Merge pull request #25 from canvas-medical/feature/jw-koala-1243

Adds Effect classes to be importable from canvas_sdk ([`e01166c`](https://github.com/canvas-medical/canvas-plugins/commit/e01166c6695d52bb716a785b872d86478b4524ff))

* Merge pull request #28 from canvas-medical/feature/jw-koala-1244-based-on-1243

Adds a BaseProtocol for inheritance ([`4355976`](https://github.com/canvas-medical/canvas-plugins/commit/435597693877da45b560a1b3d2119e4bac127bdc))

* Reverts manifest change. ([`145bf97`](https://github.com/canvas-medical/canvas-plugins/commit/145bf97af956e5b7a1f6bae3991e65c2569e16a4))

* Adds BaseProtocol and changes to RESPONDS_TO. ([`69cd602`](https://github.com/canvas-medical/canvas-plugins/commit/69cd60223f60b1b18b6aa3d273f42731f770b7c5))

* Adds missing newline. ([`de78a1e`](https://github.com/canvas-medical/canvas-plugins/commit/de78a1e29ab0b97ca220e4d1fee55480b9b862d1))

* Imports events from canvas_sdk. ([`4672038`](https://github.com/canvas-medical/canvas-plugins/commit/46720389e17b2fb2fddc0c8ec6ea56e878a07817))

* Moves generated directory and changes imports. ([`6edd6c9`](https://github.com/canvas-medical/canvas-plugins/commit/6edd6c9a6fb459c83d392fc85e6e6f842517e259))

* Removes unused import. ([`c687bb1`](https://github.com/canvas-medical/canvas-plugins/commit/c687bb13c3f2af93a160968a19086bc716b80cea))

* Removes Event import. ([`fdcc311`](https://github.com/canvas-medical/canvas-plugins/commit/fdcc3119fe5f84ae53f1e554b2d56d882ad0e595))

* Reverts extraneous changes. ([`3201103`](https://github.com/canvas-medical/canvas-plugins/commit/3201103a4eefbb2ea1308a24207704ad359f3bd9))

* Adds events imports to canvas_sdk. ([`90abef2`](https://github.com/canvas-medical/canvas-plugins/commit/90abef269e98c23bae9797126e0ec1c623e3f2ec))

* Removes typing import. ([`d753706`](https://github.com/canvas-medical/canvas-plugins/commit/d75370641e7cad6989222a5817faaf9dbd469544))

* Adds newline to end of __init__ file. ([`73e3ff1`](https://github.com/canvas-medical/canvas-plugins/commit/73e3ff1910c3be293a7a63a095c4b5fe93c2ee3c))

* Adds import for Effect from canvas_sdk. ([`0e51672`](https://github.com/canvas-medical/canvas-plugins/commit/0e5167232b3e36a2510cdd2d7d747f120300ca32))

* WIP changes to importing and using effects. ([`bd97b93`](https://github.com/canvas-medical/canvas-plugins/commit/bd97b937a4cf978d18ed12bf27bd4b633b402bba))

* Create tests for prescribe command (#24) ([`c68eabe`](https://github.com/canvas-medical/canvas-plugins/commit/c68eabe35e895b993fabaebc8b8964d5684cb993))

* Create UpdateGoal command (#19) ([`c8ae599`](https://github.com/canvas-medical/canvas-plugins/commit/c8ae599203ad272457ce26a3546e7751522bd9dd))


## v0.0.3 (2024-04-03)

### Unknown

* Create Prescribe command class (#18) ([`c4f2f36`](https://github.com/canvas-medical/canvas-plugins/commit/c4f2f36349813e4d806b07687c441cb30c63c186))

* Write integration test for command schemas

Write integration test for command schemas ([`0ad960e`](https://github.com/canvas-medical/canvas-plugins/commit/0ad960e4193225e8a2a868ae80acad0c4865b159))

* refactor tests to be more developer friendly ([`7ea4a24`](https://github.com/canvas-medical/canvas-plugins/commit/7ea4a249262e3fbfad1c3952f709a1ac93056593))

* scope token fixture to the session and add env variables ([`024ec2e`](https://github.com/canvas-medical/canvas-plugins/commit/024ec2e3b3ba625c631aaf580a38a9518cf72ba8))

* create the command within the test ([`0391ef4`](https://github.com/canvas-medical/canvas-plugins/commit/0391ef42d675aabf1a5a45ef0b4fdc308b368da8))

* update integration test to autogenerate types on our end ([`363ddd2`](https://github.com/canvas-medical/canvas-plugins/commit/363ddd217689d9e405af9d76173af6f2adbca290))

* update integration test to autogenerate types on our end ([`7db3f88`](https://github.com/canvas-medical/canvas-plugins/commit/7db3f88e0923787491c99c162e788e6ef5c31ba3))

* fix conflicts ([`ecb80bf`](https://github.com/canvas-medical/canvas-plugins/commit/ecb80bf69e348c3b625cbd37996e3ab401b21ce3))

* Merge pull request #22 from canvas-medical/ad/medication-statement-command-autocomplete

Support command autocomplete manipulation ([`d698bae`](https://github.com/canvas-medical/canvas-plugins/commit/d698bae2407069da266997f30c8cd50f5678d212))

* If we don't mark this global we're only adding to a local variable. ([`28af410`](https://github.com/canvas-medical/canvas-plugins/commit/28af41066dacc7341e9d86a4dbc67e7b66a250b4))

* Return the accumulated list of effects ([`c1bd603`](https://github.com/canvas-medical/canvas-plugins/commit/c1bd603a864cf085a64f460de029dfd3c90e74b2))

* Protocols should return pre-formed effects. ([`8632726`](https://github.com/canvas-medical/canvas-plugins/commit/8632726b7c3ce3404392dd33eb999e36cf7c553b))

* Add example plugin for command autocomplete ([`fe3adf6`](https://github.com/canvas-medical/canvas-plugins/commit/fe3adf60c090325cce83cd6962d5cd59274f2ac1))

* Add context field to event type. ([`4bf7f3b`](https://github.com/canvas-medical/canvas-plugins/commit/4bf7f3bb86a341ea4a4165de2b289ae0debf7d36))

* Add events and effects for manipulating command autocomplete results, starting with medication statement ([`5010492`](https://github.com/canvas-medical/canvas-plugins/commit/501049259eb6840e10f2e82f19837150aef8788e))

* add some TODOs and fix graceful shutdown and make RESPONDS_TO more flexible ([`0a508d2`](https://github.com/canvas-medical/canvas-plugins/commit/0a508d27dfde9ce9b49b62b82b19458ea642b94e))

* Merge pull request #16 from canvas-medical/bg-plugin-reload ([`e088c5d`](https://github.com/canvas-medical/canvas-plugins/commit/e088c5d660bdf916f72c40eecd46aad69b4720fd))

* Merge pull request #20 from canvas-medical/jw-koala-1203-based-on-bg-plugin-reload ([`36b4af3`](https://github.com/canvas-medical/canvas-plugins/commit/36b4af3cbc535827c4eca7dc69f3a445bb8e1e10))

* load plugins from disk! ([`5bec67b`](https://github.com/canvas-medical/canvas-plugins/commit/5bec67b8fefa98ed3bd4252dcc05c36a9fe39d4e))

* move custom plugins for dev ([`79218ec`](https://github.com/canvas-medical/canvas-plugins/commit/79218ec1047aedacfedff78252a9260a2bb37ab3))

* move custom plugins for dev ([`415d704`](https://github.com/canvas-medical/canvas-plugins/commit/415d704b09ce215a67bb96fe8d20e0cbb96d6b16))

* WIP ([`8952c94`](https://github.com/canvas-medical/canvas-plugins/commit/8952c948e917bc9b389b52b4eff41090bf8e25b3))

* WIP debugging code ([`2eead49`](https://github.com/canvas-medical/canvas-plugins/commit/2eead49300c6877bdee298464d457d7d5f64a016))

* WIP for module reloading ([`7169891`](https://github.com/canvas-medical/canvas-plugins/commit/716989160e61c40dd6ee6f6d4605480a2e2cdbf6))

* WIP reloading fix. ([`d193a4e`](https://github.com/canvas-medical/canvas-plugins/commit/d193a4e76fedc247789186901b297bf56f495df7))

* WIP effects and reloading. ([`33c2e2b`](https://github.com/canvas-medical/canvas-plugins/commit/33c2e2b71ca181f97f4fbd0e4b12442c35f197e1))

* Fixes plugin structure and installation issues. ([`612cacd`](https://github.com/canvas-medical/canvas-plugins/commit/612cacd24c63ad24842f903fd0f51904b57074af))

* Changes effect type. ([`82c948f`](https://github.com/canvas-medical/canvas-plugins/commit/82c948fbf59c422c3a6cd6ab527a1b6f8c652949))

* more WIP ([`216935c`](https://github.com/canvas-medical/canvas-plugins/commit/216935c84e714018ba5092969a99b680f8074c96))

* add simple module reloading ([`ea2d42a`](https://github.com/canvas-medical/canvas-plugins/commit/ea2d42a0fbe1b7cafdb9478086a1521b35481b8e))

* WIP for plugin reloading ([`caab056`](https://github.com/canvas-medical/canvas-plugins/commit/caab056024a1e7c3eeac91c0f425b07e529b04a7))

* Create Command effects and BannerAlert effects

Create Command effects and BannerAlert effects ([`89804a1`](https://github.com/canvas-medical/canvas-plugins/commit/89804a13f42a9a100f7ac51d2e7059f6a5f01afa))

* type cleanup ([`e844855`](https://github.com/canvas-medical/canvas-plugins/commit/e8448552b4797dbb02c66df212fb6faf363e24d8))

* fix plan base import ([`5e27ff0`](https://github.com/canvas-medical/canvas-plugins/commit/5e27ff047ead51411447190f0cdce049b718109c))

* feedback from demo ([`496c0c7`](https://github.com/canvas-medical/canvas-plugins/commit/496c0c7bf272fbffaf86b555fb3e9ebcf96043a9))

* also create banner alert effect ([`f36f71e`](https://github.com/canvas-medical/canvas-plugins/commit/f36f71e6888a9b3830a2d6ceba2764b6051461fa))

* create effect return values from command classes ([`c14ccad`](https://github.com/canvas-medical/canvas-plugins/commit/c14ccadbd4a9e696bd5e4f9bd8ed4f6450ca574f))

* Fix gh actions

This PR fixes the gh actions. I gave up trying to figure out how to give this repo access to the workflows repo, so i just removed any references to the actions/workflows in that repo and made everything custom in here. ([`6bccfbd`](https://github.com/canvas-medical/canvas-plugins/commit/6bccfbdddf2b19fbda6785d8633430e2cbb3bb84))

* fix one last time ([`b8d6f8a`](https://github.com/canvas-medical/canvas-plugins/commit/b8d6f8a4380144b642f78cdd6690ed99be35eae2))

* fix again ([`69cb123`](https://github.com/canvas-medical/canvas-plugins/commit/69cb123ec0bf922e61d82a7af9c69eac5810788f))

* fix pre-commit-auto-update workflow ([`c4abd7e`](https://github.com/canvas-medical/canvas-plugins/commit/c4abd7e15aad9d8beba4423701078a220ac5d0cb))

* fix the pre-commit workflow ([`5d6de3b`](https://github.com/canvas-medical/canvas-plugins/commit/5d6de3bf3a7d089d3e7bc175fe402b3b63f2b869))

* use custom gh action instead of referencing workflows repo ([`ddddc2a`](https://github.com/canvas-medical/canvas-plugins/commit/ddddc2adb4466049f7071927298d5b388ee44700))

* Merge pull request #13 from canvas-medical/feature/jw-koala-1117-canvas-plugins

Adds command-specific events ([`b5910bf`](https://github.com/canvas-medical/canvas-plugins/commit/b5910bf96daa816b686e92c015c8e5ebad024fec))

* Adds to messages. ([`73f16a7`](https://github.com/canvas-medical/canvas-plugins/commit/73f16a7a396786b54e24a6ef728f1f33137e16e5))

* Adds ASSESS_COMMAND__CONDITION_SELECTED event type. ([`d9cb3a8`](https://github.com/canvas-medical/canvas-plugins/commit/d9cb3a80f5b7f0bc588e44fb3a2a799574eab044))

* Changes events to be non-command specific. ([`ba8cbae`](https://github.com/canvas-medical/canvas-plugins/commit/ba8cbae538eed623c6ef82b789e0ca02c8861ded))

* Adds comment. ([`3423bf5`](https://github.com/canvas-medical/canvas-plugins/commit/3423bf5e674babe6205b7ce6c177158f6ce0f272))

* Adds more command types to proto messages. ([`14f3344`](https://github.com/canvas-medical/canvas-plugins/commit/14f3344e12f572a19a1fb12247e9314df8a31431))

* Adds Plan command events. ([`993f4ff`](https://github.com/canvas-medical/canvas-plugins/commit/993f4ffc797ee5690eabf7fd5f5fb61f0feb4d95))

* Create opinionated folder structure on canvas plugin init

This PR creates a clean, easy directory structure when the user does a canvas plugin init ([`c97d9f1`](https://github.com/canvas-medical/canvas-plugins/commit/c97d9f1cbd71a93ed671b3f1665705d8823caef2))

* create opinionated structure on canvas plugin init ([`103c7a9`](https://github.com/canvas-medical/canvas-plugins/commit/103c7a955760e54c705b5861bb8c964bc413920b))

* Create manifest schema and validator

This PR creates the schema and validation tools for Canvas Manifest files. There is a new cli command canvas plugin validate-manifest <package_name> which checks the manifest file to ensure it follows the schema. ([`d4287ec`](https://github.com/canvas-medical/canvas-plugins/commit/d4287ec9c06caa6a2fe5b093f21cf9ba601df1e9))

* check for jsondecodeerrors and rename to validate-manifest ([`4b84787`](https://github.com/canvas-medical/canvas-plugins/commit/4b8478715cb7e73c08583d191bdba997c83ac4e1))

* try again to fix gh workflow ([`0aaefed`](https://github.com/canvas-medical/canvas-plugins/commit/0aaefed3d0ddd154a9435fdfda4046386e21a7dd))

* fix gh workflow ([`8caeec0`](https://github.com/canvas-medical/canvas-plugins/commit/8caeec09e49f5b1fe009242a351ba9462256aea8))

* update readme ([`d9bf96f`](https://github.com/canvas-medical/canvas-plugins/commit/d9bf96fec107be2b996133b92badda34c9609121))

* create manifest schema and validator ([`7821612`](https://github.com/canvas-medical/canvas-plugins/commit/7821612ce8947dd37909477c18d4fd8e3d446b80))

* Merge pull request #9 from canvas-medical/dependabot/pip/cryptography-42.0.4

Bump cryptography from 42.0.2 to 42.0.4 ([`5f1f4cf`](https://github.com/canvas-medical/canvas-plugins/commit/5f1f4cfffe8b4bbb9a64865bc9a0d97d8115fc49))

* Bump cryptography from 42.0.2 to 42.0.4

Bumps [cryptography](https://github.com/pyca/cryptography) from 42.0.2 to 42.0.4.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/42.0.2...42.0.4)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com> ([`959705f`](https://github.com/canvas-medical/canvas-plugins/commit/959705ffc9bec35e8efdf463f2142d863ecf9b1d))

* Add more commands: Questionnaire, ReasonForVisit, StopMedication

Add more commands: Questionnaire, ReasonForVisit, StopMedication ([`292d554`](https://github.com/canvas-medical/canvas-plugins/commit/292d554c584492fac08ddc5749b027d30534aa29))

* some more cleanup ([`55bab42`](https://github.com/canvas-medical/canvas-plugins/commit/55bab42f01c494e6c053cc5528c8d4d3943e3311))

* clean up basecommand ([`6924bda`](https://github.com/canvas-medical/canvas-plugins/commit/6924bda6d637ea631ec5b9d5486f32cfb44b01ae))

* use typing_extensions instead of typing for TypedDict ([`4cc1ea4`](https://github.com/canvas-medical/canvas-plugins/commit/4cc1ea444c24439edc6ee1217549075a86aacd6d))

* create stop medication command ([`8e22cda`](https://github.com/canvas-medical/canvas-plugins/commit/8e22cda0ee2d6d61d16fa46ca3967b633c0855eb))

* create reasonforvisit ([`18b22fd`](https://github.com/canvas-medical/canvas-plugins/commit/18b22fde970dd42ddb2e83e44422709f4327d48d))

* create questionnaire ([`e76a40c`](https://github.com/canvas-medical/canvas-plugins/commit/e76a40c5f3952a86cbf56614752387c62bd4aac0))


## v0.0.2 (2024-02-23)

### Unknown

* Merge pull request #11 from canvas-medical/ad/change-runner-listening-address

Change the plugin runner to listen on 127.0.0.1 instead of [::] ([`2cdb4fb`](https://github.com/canvas-medical/canvas-plugins/commit/2cdb4fb532ac26b7757fcc71495bf7358f8a7fe6))

* Change the plugin runner to listen on 127.0.0.1 instead of [::] ([`ae6567b`](https://github.com/canvas-medical/canvas-plugins/commit/ae6567beb4f47093b8d4c67bdad5c5175f4fda9b))


## v0.0.1 (2024-02-21)

### Unknown

* Merge pull request #7 from canvas-medical/ad/add-plugin-runner-process

Add the plugin runner process ([`56ac4f5`](https://github.com/canvas-medical/canvas-plugins/commit/56ac4f5044169a82ce666b3a5903dcfc40fa9946))

* Ensure the generated classes are clearly marked as such via directory structure ([`c56f5fb`](https://github.com/canvas-medical/canvas-plugins/commit/c56f5fb0a547c4f8510f983afaf924e1ec4c4561))

* First pass at the protocol runner process. ([`dd6f9e3`](https://github.com/canvas-medical/canvas-plugins/commit/dd6f9e34092a75e13303c5e5b7e994588f3f42fb))

* Add vim swapfiles to the gitignore ([`3a85ef9`](https://github.com/canvas-medical/canvas-plugins/commit/3a85ef99d645f7e246d149dfd631830758a83498))

* Create more commands: Assess, Diagnose, Goal, HPI, MedicationStatement

Create more commands: Assess, Diagnose, Goal, HPI, MedicationStatement
and also clean up tests ([`e6dca33`](https://github.com/canvas-medical/canvas-plugins/commit/e6dca33681246daa6c0c9d94f0fbab73402604ec))

* create medication statement command ([`d580ba3`](https://github.com/canvas-medical/canvas-plugins/commit/d580ba3bb6626f0d4c6bc2e4a6d3fdc721aba0a9))

* create hpi command ([`da6b98c`](https://github.com/canvas-medical/canvas-plugins/commit/da6b98c08ba43f07d250acd9bbb2856795a0875d))

* create goal command ([`9bd89e9`](https://github.com/canvas-medical/canvas-plugins/commit/9bd89e96d45e1363f28df586a49779cb9abcb136))

* create diagnose command ([`462870d`](https://github.com/canvas-medical/canvas-plugins/commit/462870d6b75c12d2c1e11486106da537a3a6b177))

* make condition_id required ([`9b5bfb5`](https://github.com/canvas-medical/canvas-plugins/commit/9b5bfb56d72c2b627f080d7e8a1d2f101f2d7d8f))

* create assesscommand and fix up tests ([`2817bdd`](https://github.com/canvas-medical/canvas-plugins/commit/2817bdd91aed3376231e0abe09952f0ea9f6f259))

* Create strongly typed PlanCommand class

Create strongly typed PlanCommand class using pydantic ([`1f176ff`](https://github.com/canvas-medical/canvas-plugins/commit/1f176ffdf6b3d18d03cb5fb1790a034d0e7dc713))

* comments ([`c82ee5c`](https://github.com/canvas-medical/canvas-plugins/commit/c82ee5c08b98c83bec992c4681f458ee92942a72))

* use pydantic ([`95ba2d2`](https://github.com/canvas-medical/canvas-plugins/commit/95ba2d2dee2ae93fcd56d9e18d2bae3a6daf0cb1))

* clean up error messaging and remove typeddicts ([`a0ce3c7`](https://github.com/canvas-medical/canvas-plugins/commit/a0ce3c739d1c11c1afcccea4d3d42b9e77ffe05d))

* create basecommand, plancommand, and some tests ([`38004db`](https://github.com/canvas-medical/canvas-plugins/commit/38004db55c98a362fa929dc8b0d5d136c913a2d8))

* Merge pull request #5 from canvas-medical/michela/plugin_runner_init

add plugin_runner init file ([`59e7da8`](https://github.com/canvas-medical/canvas-plugins/commit/59e7da8577d1ed52385aa5fff6ec6ac5f7e21616))

* add plugin_runner init file ([`880282a`](https://github.com/canvas-medical/canvas-plugins/commit/880282a7b902954df14d2ae414e9405818681788))

* Move brush code over to canvas-cli 

This PR copies code from brush to the canvas-plugins repo, under the canvas_cli directory. It also implements github workflows. ([`731a7aa`](https://github.com/canvas-medical/canvas-plugins/commit/731a7aa4f359b8519fc24854ea79159f2ad95195))

* add precommit check ([`f8ef552`](https://github.com/canvas-medical/canvas-plugins/commit/f8ef552deadcebdd375e38ba2218e407e97d9bea))

* add python-version ([`aa2db12`](https://github.com/canvas-medical/canvas-plugins/commit/aa2db12c7b3d985948756ef68597c40291eed5d0))

* add gh workflows ([`36a017c`](https://github.com/canvas-medical/canvas-plugins/commit/36a017cddd327d3b5d66f08927ea683d73200135))

* move brush code over to canvas-cli ([`5dfdac8`](https://github.com/canvas-medical/canvas-plugins/commit/5dfdac82e5f4c59698b38bdb87c851e92a8566f5))

* Update file structure

This PR creates a new file structure for the project that follows the plans in the One SDK Refocus Readout ([`92c8bb4`](https://github.com/canvas-medical/canvas-plugins/commit/92c8bb4568d6424ba0a2bda889ac65ee6974f706))

* add the seven modules to canvas-sdk ([`b29a0fa`](https://github.com/canvas-medical/canvas-plugins/commit/b29a0faa60c6afdbca62fde2377c2266a334aab8))

* update file structure to represent new plans ([`af88c59`](https://github.com/canvas-medical/canvas-plugins/commit/af88c59f7e61bb326619beb361bd4cb060a4abf2))

* cleanup before publishing to pypi

cleanup before publishing to pypi ([`676137a`](https://github.com/canvas-medical/canvas-plugins/commit/676137ab5359b25f6d7964c524606b706914af0e))

* cleanup before publishing to pypi ([`2c30e03`](https://github.com/canvas-medical/canvas-plugins/commit/2c30e03fabbc67f6973a6b6373b75f0ece01b69e))

* Merge pull request #1 from canvas-medical/michela/koala-800-create-command

[koala-800] Build out cli functionality for auth, plugin, logging ([`d105a37`](https://github.com/canvas-medical/canvas-plugins/commit/d105a37a6ad9a6ee5ec8729ae50ccb41d060bfd5))

* build out the cli functionality ([`56e6fe3`](https://github.com/canvas-medical/canvas-plugins/commit/56e6fe396f28cf74250414ee033e14c8ee01ccd9))

* Initial commit

install canvas-core and brush

update readme

cleanup ([`96169fc`](https://github.com/canvas-medical/canvas-plugins/commit/96169fc25d4e930e86bfe939c3fc75526cc607fe))
