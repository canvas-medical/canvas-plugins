# CHANGELOG


## v0.55.0 (2025-08-19)

### Bug Fixes

- Add panel applications ([#841](https://github.com/canvas-medical/canvas-plugins/pull/841),
  [`98d4899`](https://github.com/canvas-medical/canvas-plugins/commit/98d489919a0152617aa287250c400e1a63c37df4))

### Features

- Add panel sections configuration
  ([#815](https://github.com/canvas-medical/canvas-plugins/pull/815),
  [`d080009`](https://github.com/canvas-medical/canvas-plugins/commit/d0800090607db36ae416340b9a4fa1c8d943f239))

- Add patient chart group effect ([#888](https://github.com/canvas-medical/canvas-plugins/pull/888),
  [`5f5a469`](https://github.com/canvas-medical/canvas-plugins/commit/5f5a46957d8954e8ef30d0a2cc7c87f6837522ca))


## v0.54.0 (2025-08-19)

### Bug Fixes

- Plugin_only → plugin_context ([#877](https://github.com/canvas-medical/canvas-plugins/pull/877),
  [`a221cf2`](https://github.com/canvas-medical/canvas-plugins/commit/a221cf2a24e5c67447288af99f3fe1af963cd543))

- Raise on bad status from S3 in `download_plugin`
  ([#744](https://github.com/canvas-medical/canvas-plugins/pull/744),
  [`501de93`](https://github.com/canvas-medical/canvas-plugins/commit/501de93aa6f81afc9dd78748cabcc9363fa5f667))

### Documentation

- Add better description of app launch examples
  ([#906](https://github.com/canvas-medical/canvas-plugins/pull/906),
  [`0315103`](https://github.com/canvas-medical/canvas-plugins/commit/0315103f70ed07145341a698990faa42684821d9))

### Features

- Add ConfigDict to PyDantic sandbox allowlist (koala-3196)
  ([#916](https://github.com/canvas-medical/canvas-plugins/pull/916),
  [`3d3db99`](https://github.com/canvas-medical/canvas-plugins/commit/3d3db99e7df316870298341eb760d398de74b81d))

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

Co-authored-by: marythought <10136229+marythought@users.noreply.github.com>

Co-authored-by: Beau Gunderson <beau@beaugunderson.com>

- Add warnings if many files, large files, or large total size are found
  ([#831](https://github.com/canvas-medical/canvas-plugins/pull/831),
  [`ac08059`](https://github.com/canvas-medical/canvas-plugins/commit/ac08059cb3dc31bed317fbac9fdfa684a10995c6))

- Implement custom payment processors
  ([#701](https://github.com/canvas-medical/canvas-plugins/pull/701),
  [`9974e53`](https://github.com/canvas-medical/canvas-plugins/commit/9974e53d4bc991f4958ca4ab41f18ba56ee426fc))

Co-authored-by: Miguel Quintas <miguel.quintas@canvasmedical.com>


## v0.53.2 (2025-08-12)

### Bug Fixes

- Add support for installing/uninstalling and loading/reloading a specific plugin
  ([#775](https://github.com/canvas-medical/canvas-plugins/pull/775),
  [`dcc3252`](https://github.com/canvas-medical/canvas-plugins/commit/dcc32524f5caf8d37edb45fd9f3d888dbaced066))


## v0.53.1 (2025-08-12)

### Bug Fixes

- Prevent an issue where the prescribe command effects send compound medication values where not
  desired ([#908](https://github.com/canvas-medical/canvas-plugins/pull/908),
  [`b65ece4`](https://github.com/canvas-medical/canvas-plugins/commit/b65ece4baa539516a74db1a749c14867cb12555a))


## v0.53.0 (2025-08-07)

### Features

- Add pydantic.RootModel to sandbox
  ([#898](https://github.com/canvas-medical/canvas-plugins/pull/898),
  [`780fc15`](https://github.com/canvas-medical/canvas-plugins/commit/780fc15924380cb30bc9f1a0b6920dec83aaa868))

- Add task and task comment author_id
  ([#900](https://github.com/canvas-medical/canvas-plugins/pull/900),
  [`a9fa76b`](https://github.com/canvas-medical/canvas-plugins/commit/a9fa76b2ccfadbe159ddc07535c14df47986121c))


## v0.52.0 (2025-08-06)

### Features

- Add `getattr` to sandbox ([#893](https://github.com/canvas-medical/canvas-plugins/pull/893),
  [`af653d1`](https://github.com/canvas-medical/canvas-plugins/commit/af653d1b59eb850b2fc9b6a2736c175bdd1c953a))

- Order tracking example app ([#879](https://github.com/canvas-medical/canvas-plugins/pull/879),
  [`3e99263`](https://github.com/canvas-medical/canvas-plugins/commit/3e992638558f412b55f80476061fc73a8269429e))


## v0.51.0 (2025-08-05)

### Features

- Add support for ast.Constant (ellipsis)
  ([#880](https://github.com/canvas-medical/canvas-plugins/pull/880),
  [`c089285`](https://github.com/canvas-medical/canvas-plugins/commit/c089285d2eb4d94b4051f28e2fefa410e78de774))

- Remove unused manifest data_access requirement
  ([#882](https://github.com/canvas-medical/canvas-plugins/pull/882),
  [`0282e00`](https://github.com/canvas-medical/canvas-plugins/commit/0282e004e387d8a9eecab06751a29d8f3cd7d014))


## v0.50.0 (2025-07-30)

### Documentation

- Add example plugin - Note and Commands API
  ([#833](https://github.com/canvas-medical/canvas-plugins/pull/833),
  [`f4d5567`](https://github.com/canvas-medical/canvas-plugins/commit/f4d5567ea2c7ad09f3d76867bc492bb10662fd58))

### Features

- Add compound meds model and effect
  ([#789](https://github.com/canvas-medical/canvas-plugins/pull/789),
  [`8f7e6e2`](https://github.com/canvas-medical/canvas-plugins/commit/8f7e6e25a65df7e975b71108b204d29285f602ad))

- Add events for command available actions
  ([#756](https://github.com/canvas-medical/canvas-plugins/pull/756),
  [`8c0982a`](https://github.com/canvas-medical/canvas-plugins/commit/8c0982a119c59b259b31365be252a1d99a96faa7))


## v0.49.0 (2025-07-29)

### Chores

- Add test coverage with codecov ([#864](https://github.com/canvas-medical/canvas-plugins/pull/864),
  [`b2eec06`](https://github.com/canvas-medical/canvas-plugins/commit/b2eec06d24d06cc7636a5dad95139c09dc423c95))

- Auto-update pre-commit hooks ([#865](https://github.com/canvas-medical/canvas-plugins/pull/865),
  [`49b935c`](https://github.com/canvas-medical/canvas-plugins/commit/49b935cbabb27153f4436d3e6bb182770ebe65b2))

Co-authored-by: mbiannaccone <26937791+mbiannaccone@users.noreply.github.com>

### Features

- Add additional imports from Pydantic
  ([#871](https://github.com/canvas-medical/canvas-plugins/pull/871),
  [`d34358d`](https://github.com/canvas-medical/canvas-plugins/commit/d34358d1ba8487834c5af21d7ac5f0c294a2b34c))

Co-authored-by: copilot-swe-agent[bot]

Co-authored-by: Mary Dickson <mary.dickson@canvasmedical.com>

- Add additional jwt imports for verifying tokens
  ([#863](https://github.com/canvas-medical/canvas-plugins/pull/863),
  [`5058cf5`](https://github.com/canvas-medical/canvas-plugins/commit/5058cf57aeef2c3c491b7c7e33f12e374838951c))

- Koala-3011 update plugin install text to reflect async process
  ([#738](https://github.com/canvas-medical/canvas-plugins/pull/738),
  [`b072182`](https://github.com/canvas-medical/canvas-plugins/commit/b0721825bfd5f1325f6b82219d85a52db1c77a6a))

Signed-off-by: Mary Dickson <mdickson@gmail.com>

Co-authored-by: Andrew Duane <andrew.duane@canvasmedical.com>


## v0.48.0 (2025-07-24)

### Chores

- Auto-update pre-commit hooks ([#434](https://github.com/canvas-medical/canvas-plugins/pull/434),
  [`3393db4`](https://github.com/canvas-medical/canvas-plugins/commit/3393db457f990751a9a9eb19e808b0cd1a7b67c1))

Co-authored-by: mbiannaccone <26937791+mbiannaccone@users.noreply.github.com>

### Features

- Add example patient sync plugin
  ([#724](https://github.com/canvas-medical/canvas-plugins/pull/724),
  [`339763c`](https://github.com/canvas-medical/canvas-plugins/commit/339763ca8a766ba22463b6b4e3d60f07577cb76a))

Signed-off-by: Mary Dickson <mdickson@gmail.com>

- Add Union to allowed import list
  ([#856](https://github.com/canvas-medical/canvas-plugins/pull/856),
  [`7a44a2d`](https://github.com/canvas-medical/canvas-plugins/commit/7a44a2d5ed55f9d95f8c3285e398786425728bc8))


## v0.47.0 (2025-07-23)

### Features

- Add Optional to imports ([#854](https://github.com/canvas-medical/canvas-plugins/pull/854),
  [`25e2c52`](https://github.com/canvas-medical/canvas-plugins/commit/25e2c526219905e3e4ed3a131cdc89d946783eff))


## v0.46.0 (2025-07-23)

### Bug Fixes

- Immunization statement allowed_imports
  ([#853](https://github.com/canvas-medical/canvas-plugins/pull/853),
  [`4fb2ec9`](https://github.com/canvas-medical/canvas-plugins/commit/4fb2ec92a1ea195ef1673af0eea062b3687297e2))

### Chores

- Make django models compatible with SQLite
  ([#791](https://github.com/canvas-medical/canvas-plugins/pull/791),
  [`23569ae`](https://github.com/canvas-medical/canvas-plugins/commit/23569aef5d93fd718c0f1eb0b575c24f74542299))

- Update question toggle tests to patch the correct method
  ([#852](https://github.com/canvas-medical/canvas-plugins/pull/852),
  [`851be8f`](https://github.com/canvas-medical/canvas-plugins/commit/851be8f787cf9d26046fcb2d57d651a8d6168e34))

- **ci**: Do not run pre-commit auto update action on forks
  ([#828](https://github.com/canvas-medical/canvas-plugins/pull/828),
  [`ec04c90`](https://github.com/canvas-medical/canvas-plugins/commit/ec04c9047fc15c2ac27c96dfdc8a253be0be6717))

- **tests**: Fix test settings ([#851](https://github.com/canvas-medical/canvas-plugins/pull/851),
  [`9a67afc`](https://github.com/canvas-medical/canvas-plugins/commit/9a67afc126a800131ae559145e0e133b943ab31f))

### Features

- Add cryptography dependency ([#832](https://github.com/canvas-medical/canvas-plugins/pull/832),
  [`1e4ab18`](https://github.com/canvas-medical/canvas-plugins/commit/1e4ab18b3125860995a08a4d5a68f805e612006a))

- Add support for the match operator
  ([#850](https://github.com/canvas-medical/canvas-plugins/pull/850),
  [`bf74559`](https://github.com/canvas-medical/canvas-plugins/commit/bf745592ccf97dad1262cd9c50f2c72d6afe18de))

- Create charge description master data model
  ([#778](https://github.com/canvas-medical/canvas-plugins/pull/778),
  [`50e4019`](https://github.com/canvas-medical/canvas-plugins/commit/50e40195998cb12472fe63821da0bd2c8a3ce266))

- Create new staff events ([#723](https://github.com/canvas-medical/canvas-plugins/pull/723),
  [`9e73635`](https://github.com/canvas-medical/canvas-plugins/commit/9e73635ff81de6ff9a19a322772d1a5ffff24c32))

- Grant access to patientmetadata events
  ([#830](https://github.com/canvas-medical/canvas-plugins/pull/830),
  [`2cff0b8`](https://github.com/canvas-medical/canvas-plugins/commit/2cff0b814aaafc35e17fecaf96615369442e18c5))

- Implement immunization statement command
  ([#829](https://github.com/canvas-medical/canvas-plugins/pull/829),
  [`91333d0`](https://github.com/canvas-medical/canvas-plugins/commit/91333d0c537d2d0852c2e9919bd8c171ab65439f))

- Implement question toggles for questionnaire based commands
  ([#746](https://github.com/canvas-medical/canvas-plugins/pull/746),
  [`c83b34a`](https://github.com/canvas-medical/canvas-plugins/commit/c83b34a916676262b7af7f84291baa97334cc22f))

- Save memory in plugin_runner ([#837](https://github.com/canvas-medical/canvas-plugins/pull/837),
  [`8c216b1`](https://github.com/canvas-medical/canvas-plugins/commit/8c216b16380329a04cd30c4cc4fcf29740cf1ac1))

- **events**: Add document reference events
  ([#726](https://github.com/canvas-medical/canvas-plugins/pull/726),
  [`893ee1d`](https://github.com/canvas-medical/canvas-plugins/commit/893ee1dc2692494e23415eab9acfd2b4e25ed101))

- **plugin**: Add example Footer Widget for the patient portal plugin
  ([#711](https://github.com/canvas-medical/canvas-plugins/pull/711),
  [`fb73bc2`](https://github.com/canvas-medical/canvas-plugins/commit/fb73bc2673adc52b208316080628f2f74c6f83d7))

- **plugins**: Add Patient Portal Care Team widget sample
  ([#716](https://github.com/canvas-medical/canvas-plugins/pull/716),
  [`f31dd07`](https://github.com/canvas-medical/canvas-plugins/commit/f31dd07b4402e4d8691c1ff1c38bd9792a8f2e5c))


## v0.45.0 (2025-07-17)

### Bug Fixes

- Set default pharmacy search term
  ([#777](https://github.com/canvas-medical/canvas-plugins/pull/777),
  [`134337a`](https://github.com/canvas-medical/canvas-plugins/commit/134337a08b499aa32a03111e9ac1b4054420970a))

### Features

- Add additional allowed imports for abc and typing
  ([#765](https://github.com/canvas-medical/canvas-plugins/pull/765),
  [`78caa9f`](https://github.com/canvas-medical/canvas-plugins/commit/78caa9f3a1247f18941b3de6d97b1f3848dd2ee3))

- Add note state change event models
  ([#779](https://github.com/canvas-medical/canvas-plugins/pull/779),
  [`79928a2`](https://github.com/canvas-medical/canvas-plugins/commit/79928a2125aeb3b5f8132f1aa12adbfeb1a5b31b))

- Implement vitals visualizer plugin with interactive chart and table display (koala-3030)
  ([#752](https://github.com/canvas-medical/canvas-plugins/pull/752),
  [`eacedb3`](https://github.com/canvas-medical/canvas-plugins/commit/eacedb3b62abac19b12a5b9dd61985a6f81e8f95))

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

Co-authored-by: Mary Dickson <mary.dickson@canvasmedical.com>

Co-authored-by: beaugunderson <61791+beaugunderson@users.noreply.github.com>

- **cli**: Add ability to ignore files when packaging
  ([#773](https://github.com/canvas-medical/canvas-plugins/pull/773),
  [`09d1ff4`](https://github.com/canvas-medical/canvas-plugins/commit/09d1ff4bfeaa905a16316f553914711e148ab776))


## v0.44.3 (2025-07-07)

### Bug Fixes

- Remove cert validation from pharmacy
  ([#776](https://github.com/canvas-medical/canvas-plugins/pull/776),
  [`96748e2`](https://github.com/canvas-medical/canvas-plugins/commit/96748e26138f37abdb431240a30e1a95e63bf4ce))


## v0.44.2 (2025-07-04)

### Bug Fixes

- Env var and default url for pharmacy service
  ([#770](https://github.com/canvas-medical/canvas-plugins/pull/770),
  [`bd88b05`](https://github.com/canvas-medical/canvas-plugins/commit/bd88b05f31f8d5798b2a0c2c187fb8dff3100e9c))


## v0.44.1 (2025-07-03)

### Bug Fixes

- Fix InstallmentPlan data model ([#755](https://github.com/canvas-medical/canvas-plugins/pull/755),
  [`c6b1f58`](https://github.com/canvas-medical/canvas-plugins/commit/c6b1f583c73bead98e0040b46df424ed02b23a86))


## v0.44.0 (2025-07-03)

### Chores

- Create patient portal appointment filter plugin example
  ([#718](https://github.com/canvas-medical/canvas-plugins/pull/718),
  [`0d5ec9d`](https://github.com/canvas-medical/canvas-plugins/commit/0d5ec9dd1d6a77bf6af9f3cdc962a7208b75b8ce))

Signed-off-by: Nuno Silva <nuno.silva@glazedsolutions.com>

Co-authored-by: Mary Dickson <mdickson@gmail.com>

### Features

- Add businessline, patientconsent, payorspecificcharge to data module
  ([#704](https://github.com/canvas-medical/canvas-plugins/pull/704),
  [`4409ee8`](https://github.com/canvas-medical/canvas-plugins/commit/4409ee890bf8d2ac5aa1811e3ec913997fa7af39))

Signed-off-by: Michela Iannaccone <mbiannaccone@gmail.com>

- Add Patient Portal Plugin with Header Widget
  ([#697](https://github.com/canvas-medical/canvas-plugins/pull/697),
  [`db9f33d`](https://github.com/canvas-medical/canvas-plugins/commit/db9f33df972985010197487a0be4f26772f48589))

- Add simple Canvas plugin example with note header button and hello world UI
  ([#740](https://github.com/canvas-medical/canvas-plugins/pull/740),
  [`c13fed1`](https://github.com/canvas-medical/canvas-plugins/commit/c13fed14ef0377c42c8670f965f02f1b8ea21b4b))

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

Co-authored-by: marythought <10136229+marythought@users.noreply.github.com>

- Add user last invite date time field
  ([#646](https://github.com/canvas-medical/canvas-plugins/pull/646),
  [`849be63`](https://github.com/canvas-medical/canvas-plugins/commit/849be63ff7ed3207fe10012662146fe85b3ce80b))

- Implement effects for updating and deleting/cancelling notes, appointments, and schedule events
  ([#712](https://github.com/canvas-medical/canvas-plugins/pull/712),
  [`61df2ac`](https://github.com/canvas-medical/canvas-plugins/commit/61df2acaf385f95f1506d80c684c9f2074ac5ebf))

Signed-off-by: Nuno Silva <nuno.silva@glazedsolutions.com>

Co-authored-by: José Magalhães <jose.magalhaes@canvasmedical.com>

- **cli**: Replace keyring with file-based token storage
  ([#725](https://github.com/canvas-medical/canvas-plugins/pull/725),
  [`70c0c77`](https://github.com/canvas-medical/canvas-plugins/commit/70c0c77d97e3bf9f48f2a41d3919405e9d68f82f))


## v0.43.0 (2025-07-01)

### Features

- Add can_be_snoozed to ProtocolCard
  ([#657](https://github.com/canvas-medical/canvas-plugins/pull/657),
  [`55566dc`](https://github.com/canvas-medical/canvas-plugins/commit/55566dc1596135c0cad49aacb07044be59210d82))

- Add claim and associated data modules
  ([#638](https://github.com/canvas-medical/canvas-plugins/pull/638),
  [`bbef4c5`](https://github.com/canvas-medical/canvas-plugins/commit/bbef4c51c6f4b37f12e3908e0e846ec4d0643abb))

- Add missing `surgical` field to Condition model (KOALA-3001)
  ([#714](https://github.com/canvas-medical/canvas-plugins/pull/714),
  [`12a9418`](https://github.com/canvas-medical/canvas-plugins/commit/12a94185e519d2b97065307078af76c7de5f6c44))

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

Co-authored-by: marythought <10136229+marythought@users.noreply.github.com>

- Add new external id creation effect
  ([#702](https://github.com/canvas-medical/canvas-plugins/pull/702),
  [`6ff9986`](https://github.com/canvas-medical/canvas-plugins/commit/6ff9986260b82e95aac345f27b3f4ab2a14576d4))

Signed-off-by: Mary Dickson <mary.dickson@canvasmedical.com>

- Add patient external id to patient effect
  ([#685](https://github.com/canvas-medical/canvas-plugins/pull/685),
  [`3258054`](https://github.com/canvas-medical/canvas-plugins/commit/3258054819b3a9c93ee7d892e0a3e2bea1f22ac2))

- Expose a pharmacy search view ([#727](https://github.com/canvas-medical/canvas-plugins/pull/727),
  [`27950eb`](https://github.com/canvas-medical/canvas-plugins/commit/27950ebaf95cdcbdb5092d3792e5bc44efa8fcae))

- Filter not available providers in appointments search form
  ([#719](https://github.com/canvas-medical/canvas-plugins/pull/719),
  [`3fcd348`](https://github.com/canvas-medical/canvas-plugins/commit/3fcd348c3c9ed3824e3b2e35919e0cb391d4a582))

### Refactoring

- Update HTTP utils for accessing science and ontologies to use ENV variables
  ([#717](https://github.com/canvas-medical/canvas-plugins/pull/717),
  [`c4f7f94`](https://github.com/canvas-medical/canvas-plugins/commit/c4f7f94a58f483278232b30f7a28d88c011ab889))


## v0.42.0 (2025-06-18)

### Chores

- Rename the test-plugins/ directory to example-plugins/ to clarify they are not part of any
  automated tests ([#703](https://github.com/canvas-medical/canvas-plugins/pull/703),
  [`4ea8ad6`](https://github.com/canvas-medical/canvas-plugins/commit/4ea8ad69bca763bfb323111a6ede8b8e9ae8cb5f))

### Documentation

- Add example plugin for SimpleAPI
  ([#456](https://github.com/canvas-medical/canvas-plugins/pull/456),
  [`2a115d4`](https://github.com/canvas-medical/canvas-plugins/commit/2a115d4cd8d3b4bfb996bd39459cade1486a0fe8))

### Features

- Implement patient metadata upsert effect
  ([#673](https://github.com/canvas-medical/canvas-plugins/pull/673),
  [`1f15e44`](https://github.com/canvas-medical/canvas-plugins/commit/1f15e44a4240b550178af2b32b165bfd679d76da))


## v0.41.0 (2025-06-13)

### Documentation

- Add more example plugins ([#687](https://github.com/canvas-medical/canvas-plugins/pull/687),
  [`8c9dadf`](https://github.com/canvas-medical/canvas-plugins/commit/8c9dadfc7edcbe8babd570b54ed333983867d1a7))

### Features

- Export installed SDK version ([#654](https://github.com/canvas-medical/canvas-plugins/pull/654),
  [`d9dbb49`](https://github.com/canvas-medical/canvas-plugins/commit/d9dbb4940fa75401a9eefa9d712e01eba2713e7b))


## v0.40.1 (2025-06-10)

### Bug Fixes

- Allow non-protocol imports, add tests
  ([#677](https://github.com/canvas-medical/canvas-plugins/pull/677),
  [`98a2c61`](https://github.com/canvas-medical/canvas-plugins/commit/98a2c61b95081cc792cdcba41a0266c839a98870))


## v0.40.0 (2025-06-10)

### Bug Fixes

- Correct a typo ([#663](https://github.com/canvas-medical/canvas-plugins/pull/663),
  [`964b60b`](https://github.com/canvas-medical/canvas-plugins/commit/964b60b49a7f5c3db18b45c6307be268ac391f01))

### Features

- Add `cast` to allowed imports ([#666](https://github.com/canvas-medical/canvas-plugins/pull/666),
  [`e0be57d`](https://github.com/canvas-medical/canvas-plugins/commit/e0be57dc9b0f42b41bb3bdb67c059f5621184e12))

- Add PLUGIN_POOL_DEBUG and thread_cleanup
  ([#637](https://github.com/canvas-medical/canvas-plugins/pull/637),
  [`ba3902d`](https://github.com/canvas-medical/canvas-plugins/commit/ba3902d719d1568951fda23de823795acef127fe))


## v0.39.0 (2025-06-04)

### Bug Fixes

- Generate protobufs ([#662](https://github.com/canvas-medical/canvas-plugins/pull/662),
  [`f3bb504`](https://github.com/canvas-medical/canvas-plugins/commit/f3bb504c05d5ebd5530cdfa08fed2e12756a81b8))

- Reduce ValueSet memory usage ([#655](https://github.com/canvas-medical/canvas-plugins/pull/655),
  [`34d0369`](https://github.com/canvas-medical/canvas-plugins/commit/34d0369193eee98de5f037d3ae8c87dd10ee08c7))

### Features

- Add can_be_snoozed attribute to ProtocolCard
  ([#639](https://github.com/canvas-medical/canvas-plugins/pull/639),
  [`4e04612`](https://github.com/canvas-medical/canvas-plugins/commit/4e04612ae115fadb0dc18b0af8fa71baaeea709b))

- Add create form effect and patient metadata data module
  ([#624](https://github.com/canvas-medical/canvas-plugins/pull/624),
  [`3f58aac`](https://github.com/canvas-medical/canvas-plugins/commit/3f58aac56946dcfef84eac0aead7245c2b4caba2))

- Add launch modal title property
  ([#635](https://github.com/canvas-medical/canvas-plugins/pull/635),
  [`2bf9047`](https://github.com/canvas-medical/canvas-plugins/commit/2bf90476c05de911c7459274f944cf90a9527340))

- Add message effects ([#567](https://github.com/canvas-medical/canvas-plugins/pull/567),
  [`69d8a4f`](https://github.com/canvas-medical/canvas-plugins/commit/69d8a4f243cdb05e6338fb2f5950b82b776c1d68))

- Patient external identifier events
  ([#630](https://github.com/canvas-medical/canvas-plugins/pull/630),
  [`894ad12`](https://github.com/canvas-medical/canvas-plugins/commit/894ad123c85076959cbcdf0ed20ce5f6840af50a))

Signed-off-by: Nuno Silva <nuno.silva@canvasmedical.com>

Co-authored-by: Nuno Silva <nuno.silva@canvasmedical.com>


## v0.38.0 (2025-05-30)

### Bug Fixes

- Add missing Sentry tags ([#636](https://github.com/canvas-medical/canvas-plugins/pull/636),
  [`75f19b5`](https://github.com/canvas-medical/canvas-plugins/commit/75f19b5c63a1ea1caa792247076f4d16190ed089))

### Features

- Add staff addresses and photos to data module
  ([#621](https://github.com/canvas-medical/canvas-plugins/pull/621),
  [`3038df7`](https://github.com/canvas-medical/canvas-plugins/commit/3038df733b8a7256fa093975a20fefe85acf3991))


## v0.37.0 (2025-05-21)

### Documentation

- Add example application plugins
  ([#622](https://github.com/canvas-medical/canvas-plugins/pull/622),
  [`6170320`](https://github.com/canvas-medical/canvas-plugins/commit/6170320bd0e69302bd0cf574aa4d415ddbd25a63))

### Features

- Add new events for supervising provider post/pre search and allow prescribe command to set
  supervising provider ([#527](https://github.com/canvas-medical/canvas-plugins/pull/527),
  [`f3581f0`](https://github.com/canvas-medical/canvas-plugins/commit/f3581f00d916377af459dcd562c29633f7259ea3))


## v0.36.0 (2025-05-16)

### Bug Fixes

- Don't copy locals(), prevents additional memory usage
  ([#605](https://github.com/canvas-medical/canvas-plugins/pull/605),
  [`8b7b26f`](https://github.com/canvas-medical/canvas-plugins/commit/8b7b26f0192a88ec3deb627c08dbf5fbcf2f0c0e))

- Ensure that meta props still get created for cqms where type annotations are included
  ([#566](https://github.com/canvas-medical/canvas-plugins/pull/566),
  [`0cf38d1`](https://github.com/canvas-medical/canvas-plugins/commit/0cf38d1f20fa3532addba3ca50abe6d2476f4a77))

### Features

- Add chart section review command
  ([#537](https://github.com/canvas-medical/canvas-plugins/pull/537),
  [`16f2f8b`](https://github.com/canvas-medical/canvas-plugins/commit/16f2f8b18b5be6aa6e34654a030f0e94b73c5a8d))

- Add provider companion specific scope to applications
  ([#533](https://github.com/canvas-medical/canvas-plugins/pull/533),
  [`cf86041`](https://github.com/canvas-medical/canvas-plugins/commit/cf86041bedb90947adc4fad502e1cabfed2e77f5))

- Implement Caching API ([#561](https://github.com/canvas-medical/canvas-plugins/pull/561),
  [`f39aabf`](https://github.com/canvas-medical/canvas-plugins/commit/f39aabf0ec154eb43938ea5eb4e0cec4b00f1971))

- Launch modal effect improvements
  ([#588](https://github.com/canvas-medical/canvas-plugins/pull/588),
  [`bb795f8`](https://github.com/canvas-medical/canvas-plugins/commit/bb795f87ce73b69ba435fb84ec279ed03c76970a))

- Websockets API ([#606](https://github.com/canvas-medical/canvas-plugins/pull/606),
  [`90f2686`](https://github.com/canvas-medical/canvas-plugins/commit/90f2686a40a818a6336d095a83568746d0dab293))


## v0.35.1 (2025-05-13)

### Bug Fixes

- Remove event_handler_count to keep influx from exploding
  ([#602](https://github.com/canvas-medical/canvas-plugins/pull/602),
  [`9c9cf21`](https://github.com/canvas-medical/canvas-plugins/commit/9c9cf215270f0ddc7b241af2f3e91b40e5e6d83b))

- Replace use of the gRPC AsyncIO API with the gRPC standard API
  ([#575](https://github.com/canvas-medical/canvas-plugins/pull/575),
  [`71234b3`](https://github.com/canvas-medical/canvas-plugins/commit/71234b34bc715684e14fd5317f4a4d8b966e4c55))

Signed-off-by: Christopher Sande <christopher.sande@canvasmedical.com>


## v0.35.0 (2025-05-07)

### Chores

- Add plugin metrics ([#532](https://github.com/canvas-medical/canvas-plugins/pull/532),
  [`1e7dcab`](https://github.com/canvas-medical/canvas-plugins/commit/1e7dcab6b1c7421dca439c9669d785c5a45f3dac))

- **tests**: Increase wait time for plugin installation
  ([#578](https://github.com/canvas-medical/canvas-plugins/pull/578),
  [`cc4afd0`](https://github.com/canvas-medical/canvas-plugins/commit/cc4afd0d4f1aed600cd00e13c4a8bc42e60c5827))

### Features

- Add "Change Medication" command
  ([#543](https://github.com/canvas-medical/canvas-plugins/pull/543),
  [`ef726dd`](https://github.com/canvas-medical/canvas-plugins/commit/ef726dd8a1f24ab01aa4288d7e33a5ad26af0dcc))

- Add Create Patient effect ([#535](https://github.com/canvas-medical/canvas-plugins/pull/535),
  [`930a4b1`](https://github.com/canvas-medical/canvas-plugins/commit/930a4b19d71d4cb8b65cfe713c983b3227279ed5))

- Add message to data module ([#542](https://github.com/canvas-medical/canvas-plugins/pull/542),
  [`945e0e2`](https://github.com/canvas-medical/canvas-plugins/commit/945e0e265a1e0bcd8cc7be09151e2bcddf300327))

- Allow importing ZoneInfo ([#585](https://github.com/canvas-medical/canvas-plugins/pull/585),
  [`5e7e30e`](https://github.com/canvas-medical/canvas-plugins/commit/5e7e30efb06d5f2ddbdd88fb6b4c9efd86732c42))

### Refactoring

- Canvas-plugins test suite ([#497](https://github.com/canvas-medical/canvas-plugins/pull/497),
  [`42083de`](https://github.com/canvas-medical/canvas-plugins/commit/42083deac2c41f31e5f6d3250a56ed9277af20f2))


## v0.34.1 (2025-05-01)

### Bug Fixes

- Un-break sandbox dictionary and list access
  ([#577](https://github.com/canvas-medical/canvas-plugins/pull/577),
  [`4907d22`](https://github.com/canvas-medical/canvas-plugins/commit/4907d22596ae98125c5971339e80843fbb5386c2))


## v0.34.0 (2025-04-28)

### Features

- Add JsonOnlyResponse and a test for ontologies_http
  ([#564](https://github.com/canvas-medical/canvas-plugins/pull/564),
  [`9414ef7`](https://github.com/canvas-medical/canvas-plugins/commit/9414ef71f21c73f510ce5a682cb2d4eb23640658))


## v0.33.1 (2025-04-24)

### Bug Fixes

- Remove duplicate question append
  ([#530](https://github.com/canvas-medical/canvas-plugins/pull/530),
  [`dbac2f4`](https://github.com/canvas-medical/canvas-plugins/commit/dbac2f4f18785a354ce3ef0eda0da01f7f7fb7a2))

- Sandbox security improvements ([#529](https://github.com/canvas-medical/canvas-plugins/pull/529),
  [`98ddf62`](https://github.com/canvas-medical/canvas-plugins/commit/98ddf6277f2ec5dc310bd346dc546ae2cc76282b))

Co-authored-by: Beau Gunderson <beau@beaugunderson.com>

Co-authored-by: David Jantzen <mr.djantzen@gmail.com>


## v0.33.0 (2025-04-17)

### Features

- Add portal section to patient profile configuration
  ([#417](https://github.com/canvas-medical/canvas-plugins/pull/417),
  [`d253ceb`](https://github.com/canvas-medical/canvas-plugins/commit/d253ceb94ab4217c728dc12dfb25dcf0f4b29e4f))

- Add update_user and patient_portal_send_invite effects
  ([#470](https://github.com/canvas-medical/canvas-plugins/pull/470),
  [`0584714`](https://github.com/canvas-medical/canvas-plugins/commit/0584714b93dbf5fe1c46a1769c5b42fdb4f2529a))


## v0.32.0 (2025-04-11)

### Bug Fixes

- Add missing events ([#521](https://github.com/canvas-medical/canvas-plugins/pull/521),
  [`20ced4e`](https://github.com/canvas-medical/canvas-plugins/commit/20ced4ee9c937c4f8afd4a07d7c64844eb4937d1))

### Features

- Add Sentry logging ([#410](https://github.com/canvas-medical/canvas-plugins/pull/410),
  [`e064b4c`](https://github.com/canvas-medical/canvas-plugins/commit/e064b4ca9f308d4105d634c1966968b4852a45f2))


## v0.31.0 (2025-04-08)

### Bug Fixes

- Don't block for Redis messages ([#516](https://github.com/canvas-medical/canvas-plugins/pull/516),
  [`6f87f0c`](https://github.com/canvas-medical/canvas-plugins/commit/6f87f0c76673dd1b4ad6d72fbacb3e571c3242d9))

### Features

- Add all protocol card statuses ([#468](https://github.com/canvas-medical/canvas-plugins/pull/468),
  [`26521ad`](https://github.com/canvas-medical/canvas-plugins/commit/26521ad9ee9bd9f12a2edc5a777faecf5ef98623))

- Add environment dict containing the customer identifier to plugin handler scope
  ([#513](https://github.com/canvas-medical/canvas-plugins/pull/513),
  [`d23cfd9`](https://github.com/canvas-medical/canvas-plugins/commit/d23cfd9bea7a3d86746f3d36b00669b89cbada27))

- Add session based auth to simpleapi
  ([#495](https://github.com/canvas-medical/canvas-plugins/pull/495),
  [`3b2b96a`](https://github.com/canvas-medical/canvas-plugins/commit/3b2b96a4cad62aca539c7681fbced5c93fcc7973))


## v0.30.0 (2025-04-02)

### Features

- Allow iframes to request the camera permission
  ([#510](https://github.com/canvas-medical/canvas-plugins/pull/510),
  [`6c05a6f`](https://github.com/canvas-medical/canvas-plugins/commit/6c05a6fb166b01e0c90b63ced1a4bd83165b9e78))


## v0.29.1 (2025-03-31)

### Bug Fixes

- Make path matching regex compatible with root paths ('/')
  ([#505](https://github.com/canvas-medical/canvas-plugins/pull/505),
  [`1719cca`](https://github.com/canvas-medical/canvas-plugins/commit/1719cca3ad18917267fb7692826febb3758a323c))

Co-authored-by: Christopher Sande <christopher.sande@canvasmedical.com>


## v0.29.0 (2025-03-27)

### Features

- Add events and effect to configure patient portal join and book buttons
  ([#487](https://github.com/canvas-medical/canvas-plugins/pull/487),
  [`fcf397d`](https://github.com/canvas-medical/canvas-plugins/commit/fcf397ddbd24a22f7573a7d51e1674da7f83d32d))

- Add service secrets to the plugin runner
  ([#480](https://github.com/canvas-medical/canvas-plugins/pull/480),
  [`d9483ef`](https://github.com/canvas-medical/canvas-plugins/commit/d9483ef2f6f69b08257dfbd20e23481afeb8882d))

- Match SimpleAPI URLs with path patterns
  ([#457](https://github.com/canvas-medical/canvas-plugins/pull/457),
  [`6e118eb`](https://github.com/canvas-medical/canvas-plugins/commit/6e118ebd27895b4203b77316a1705400b1990bce))


## v0.28.0 (2025-03-20)

### Bug Fixes

- Allow originating perform without data
  ([#492](https://github.com/canvas-medical/canvas-plugins/pull/492),
  [`ea72158`](https://github.com/canvas-medical/canvas-plugins/commit/ea7215812ed0913d46c3ee7161b0facf8f0c3d24))

- Improve validation rules for new url_permissions format
  ([#448](https://github.com/canvas-medical/canvas-plugins/pull/448),
  [`d0e122a`](https://github.com/canvas-medical/canvas-plugins/commit/d0e122a996cfa377e061fd1a4dc957499ca4f00d))

### Features

- Add banner alerts to data module
  ([#485](https://github.com/canvas-medical/canvas-plugins/pull/485),
  [`fba170a`](https://github.com/canvas-medical/canvas-plugins/commit/fba170a8ee397ff70ba1ac1d9a84d087728b8f32))

- Add priority to action buttons ([#478](https://github.com/canvas-medical/canvas-plugins/pull/478),
  [`01ff1d0`](https://github.com/canvas-medical/canvas-plugins/commit/01ff1d02a09f9c03b33c8a618b971fe9f682c2d1))

- Uncomment ordering_provider ([#473](https://github.com/canvas-medical/canvas-plugins/pull/473),
  [`a59456d`](https://github.com/canvas-medical/canvas-plugins/commit/a59456db685eb191751fe6009a9b40adff919a65))

Signed-off-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com>

Co-authored-by: Beau Gunderson <beau@beaugunderson.com>


## v0.27.0 (2025-03-10)

### Features

- Added a method to the SimpleAPI request class that can parse form data request bodies
  ([#453](https://github.com/canvas-medical/canvas-plugins/pull/453),
  [`946a26a`](https://github.com/canvas-medical/canvas-plugins/commit/946a26a80fdb3e194f6bc1d50b63070cf458032e))

Signed-off-by: Christopher Sande <christopher.sande@canvasmedical.com>

- Allow importing jwt in the plugin runner sandbox
  ([#454](https://github.com/canvas-medical/canvas-plugins/pull/454),
  [`59deb88`](https://github.com/canvas-medical/canvas-plugins/commit/59deb88a769c4abded9a4b4bfd9f050a12d3ad5c))

### Refactoring

- Change SimpleAPI request headers and query parameters to be a multidict structure
  ([#455](https://github.com/canvas-medical/canvas-plugins/pull/455),
  [`43f71d9`](https://github.com/canvas-medical/canvas-plugins/commit/43f71d9f5f0b05f0c639dcdafdbbf88c719a823d))

Signed-off-by: Christopher Sande <christopher.sande@canvasmedical.com>

- Moved construction of SimpleAPI route registry to __init_subclass__
  ([#450](https://github.com/canvas-medical/canvas-plugins/pull/450),
  [`9704a44`](https://github.com/canvas-medical/canvas-plugins/commit/9704a44161505dfb209b9ea72cdfe0bb5ead22a0))

Signed-off-by: Christopher Sande <csande@gmail.com>

Co-authored-by: Nuno Silva <nuno.silva@canvasmedical.com>


## v0.26.0 (2025-03-05)

### Features

- Adds a StaffContactPoint data module model
  ([#452](https://github.com/canvas-medical/canvas-plugins/pull/452),
  [`412b0c4`](https://github.com/canvas-medical/canvas-plugins/commit/412b0c406db1a5e13cdb1581adb3f54d19e6d057))

- Adds AppointmentExternalIdentifier model to data module
  ([#451](https://github.com/canvas-medical/canvas-plugins/pull/451),
  [`17367ab`](https://github.com/canvas-medical/canvas-plugins/commit/17367aba448d99ecf17ef507fcaf74ad41318c52))

### Testing

- Ensure PLUGINS_DIR exists before being added to sys.path
  ([#446](https://github.com/canvas-medical/canvas-plugins/pull/446),
  [`4600d44`](https://github.com/canvas-medical/canvas-plugins/commit/4600d44b95cfae8d7864b2212538977cf519e8e4))


## v0.25.0 (2025-02-28)

### Features

- Plugins custom API handlers ([#382](https://github.com/canvas-medical/canvas-plugins/pull/382),
  [`e3f2bd3`](https://github.com/canvas-medical/canvas-plugins/commit/e3f2bd3fed605f1c4194dae8f189324ec9ec2d9c))

Co-authored-by: José Magalhães <jose.magalhaes@canvasmedical.com>


## v0.24.0 (2025-02-27)

### Features

- Add iframe permissions support ([#399](https://github.com/canvas-medical/canvas-plugins/pull/399),
  [`f51b349`](https://github.com/canvas-medical/canvas-plugins/commit/f51b349f98096b509028316e0a8e47c44f0ed4d9))

Co-authored-by: Andrew Duane <andrew.duane@canvasmedical.com>


## v0.23.0 (2025-02-27)

### Bug Fixes

- Refactor intake forms to be just forms
  ([#439](https://github.com/canvas-medical/canvas-plugins/pull/439),
  [`2fe3e89`](https://github.com/canvas-medical/canvas-plugins/commit/2fe3e897463096a09b0747677c67a5ece262977d))

### Features

- Add menu and widgets events and effects
  ([#424](https://github.com/canvas-medical/canvas-plugins/pull/424),
  [`33509c8`](https://github.com/canvas-medical/canvas-plugins/commit/33509c85c786cba00dbde8afbdc6fabffd1b4cbb))

Co-authored-by: Rui Batista <rui.batista@canvasmedical.com>


## v0.22.1 (2025-02-25)

### Bug Fixes

- Reconnect to database when connection is lost
  ([#436](https://github.com/canvas-medical/canvas-plugins/pull/436),
  [`50efabc`](https://github.com/canvas-medical/canvas-plugins/commit/50efabcf5ab3c7d7794f902dc9c019acdc11e8c8))


## v0.22.0 (2025-02-21)

### Bug Fixes

- Add missing commands to module init
  ([#435](https://github.com/canvas-medical/canvas-plugins/pull/435),
  [`f178471`](https://github.com/canvas-medical/canvas-plugins/commit/f178471792631aa2eb3a67aca0c00907f6d75559))

- Allow setting lab partner by name or as None
  ([#429](https://github.com/canvas-medical/canvas-plugins/pull/429),
  [`f90733c`](https://github.com/canvas-medical/canvas-plugins/commit/f90733c52c68d7fe5722c526bd780591290177c6))

### Features

- Add imaging order command ([#396](https://github.com/canvas-medical/canvas-plugins/pull/396),
  [`8b7d10d`](https://github.com/canvas-medical/canvas-plugins/commit/8b7d10d7004b5daafde48b8059598ab14e82933a))

- Add instruct command ([#425](https://github.com/canvas-medical/canvas-plugins/pull/425),
  [`93aa066`](https://github.com/canvas-medical/canvas-plugins/commit/93aa0665ccddd502934aadb39597d1f3ad1e1710))

- Add refer command ([#430](https://github.com/canvas-medical/canvas-plugins/pull/430),
  [`eb36f9c`](https://github.com/canvas-medical/canvas-plugins/commit/eb36f9c129b57462effb94d383ab30d39808badb))

- Add resolve condition command ([#428](https://github.com/canvas-medical/canvas-plugins/pull/428),
  [`ba86b9b`](https://github.com/canvas-medical/canvas-plugins/commit/ba86b9b662e892c09ac31ea0f4aecee382688b4c))

- Adjustprescription command ([#432](https://github.com/canvas-medical/canvas-plugins/pull/432),
  [`8a84c46`](https://github.com/canvas-medical/canvas-plugins/commit/8a84c4609e745d6904e7258d4f425de8c547f554))

- Implement adding questionnaire responses
  ([#431](https://github.com/canvas-medical/canvas-plugins/pull/431),
  [`a36c136`](https://github.com/canvas-medical/canvas-plugins/commit/a36c1368f197659aaa41793043b818c27f3a4f15))


## v0.21.0 (2025-02-19)

### Bug Fixes

- Lab order command validations ([#423](https://github.com/canvas-medical/canvas-plugins/pull/423),
  [`45376f1`](https://github.com/canvas-medical/canvas-plugins/commit/45376f1562b455871fd997b6a5128768110583dc))

### Features

- Create effects for billinglineitems
  ([#418](https://github.com/canvas-medical/canvas-plugins/pull/418),
  [`d8b9187`](https://github.com/canvas-medical/canvas-plugins/commit/d8b91876478f07771097f841aa015bdc8128f3df))

Signed-off-by: Michela Iannaccone <mbiannaccone@gmail.com>


## v0.20.0 (2025-02-18)

### Bug Fixes

- Refactor command values into dynamic method
  ([#415](https://github.com/canvas-medical/canvas-plugins/pull/415),
  [`09527d3`](https://github.com/canvas-medical/canvas-plugins/commit/09527d3367a57effabd40a4a0d32cf92e9837481))

### Chores

- **metrics**: Log nr event handlers
  ([#416](https://github.com/canvas-medical/canvas-plugins/pull/416),
  [`43e1f4d`](https://github.com/canvas-medical/canvas-plugins/commit/43e1f4d3cfaf597cbb33034b14ff90a5360ac438))

### Features

- Add follow-up command ([#409](https://github.com/canvas-medical/canvas-plugins/pull/409),
  [`9a3eb4e`](https://github.com/canvas-medical/canvas-plugins/commit/9a3eb4edcb6862a8399a1adfc4267ace4f6a0e92))

- Add new target option to LaunchModalEffect
  ([#414](https://github.com/canvas-medical/canvas-plugins/pull/414),
  [`82728dc`](https://github.com/canvas-medical/canvas-plugins/commit/82728dcf4be2f9d6604bdcf6f822de282119a6f1))

- Add partner lab models and update lab order command to validate results
  ([#404](https://github.com/canvas-medical/canvas-plugins/pull/404),
  [`e692077`](https://github.com/canvas-medical/canvas-plugins/commit/e692077ab1b71b0c3341b90e237e3d86f0dea3a1))

- Improve logging ([#413](https://github.com/canvas-medical/canvas-plugins/pull/413),
  [`46d99b4`](https://github.com/canvas-medical/canvas-plugins/commit/46d99b4ffe1e3564aa8911693624ccbc027c510b))


## v0.19.1 (2025-02-13)

### Bug Fixes

- Refactor database code and remove from canvas_sdk.utils.db
  ([#411](https://github.com/canvas-medical/canvas-plugins/pull/411),
  [`28b4b0b`](https://github.com/canvas-medical/canvas-plugins/commit/28b4b0bcc09d9f548f58261b1939d619ea075d7d))


## v0.19.0 (2025-02-12)

### Bug Fixes

- Accept UUID type for rfv coding field
  ([#407](https://github.com/canvas-medical/canvas-plugins/pull/407),
  [`c5bcd9e`](https://github.com/canvas-medical/canvas-plugins/commit/c5bcd9ec8e4290ddbd19343151ef72c5a27aaad2))

### Features

- Create BillingLineItemModifier data class
  ([#393](https://github.com/canvas-medical/canvas-plugins/pull/393),
  [`130e55a`](https://github.com/canvas-medical/canvas-plugins/commit/130e55ab9a4c8feb31d547b721db0f33ed96a004))

- Implement reason for visit codings with validations for rfv command
  ([#392](https://github.com/canvas-medical/canvas-plugins/pull/392),
  [`804e59f`](https://github.com/canvas-medical/canvas-plugins/commit/804e59f7281902bc563520b3248ca6dac8ab84e7))

- Install questionnaires via plugins
  ([#369](https://github.com/canvas-medical/canvas-plugins/pull/369),
  [`0433a3e`](https://github.com/canvas-medical/canvas-plugins/commit/0433a3eec48f404eabc76445198c634f55c5c6b9))


## v0.18.0 (2025-02-05)

### Bug Fixes

- Add CANCEL_PRESCRIPTION, SNOOZE_PROTOCOL, UPDATE_DIAGNOSIS command events
  ([#386](https://github.com/canvas-medical/canvas-plugins/pull/386),
  [`d804f2b`](https://github.com/canvas-medical/canvas-plugins/commit/d804f2b5033a9b043378870f6284a954453d5e24))

### Features

- Add force option when uninstalling a plugin
  ([#276](https://github.com/canvas-medical/canvas-plugins/pull/276),
  [`6a861c6`](https://github.com/canvas-medical/canvas-plugins/commit/6a861c64c7022cc6028b777741b6b1f23e35a546))

- Added team identifier to the AddTask and UpdateTask effects
  ([#362](https://github.com/canvas-medical/canvas-plugins/pull/362),
  [`aaddfe8`](https://github.com/canvas-medical/canvas-plugins/commit/aaddfe8b936cf5743259ce4770dfd1f076ac54c3))

- Added Team models to SDK data module
  ([#349](https://github.com/canvas-medical/canvas-plugins/pull/349),
  [`096ce23`](https://github.com/canvas-medical/canvas-plugins/commit/096ce2307fc2de0eb8f4db04f9708e12b2e5f24a))

- Helper method on Http to execute HTTP requests in parallel
  ([#376](https://github.com/canvas-medical/canvas-plugins/pull/376),
  [`2317dd9`](https://github.com/canvas-medical/canvas-plugins/commit/2317dd94c6a3617d3e9c0214a22e81d602e4ee1c))

Signed-off-by: Christopher Sande <csande@gmail.com>

Co-authored-by: José Magalhães <jose.magalhaes@canvasmedical.com>


## v0.17.0 (2025-02-04)

### Bug Fixes

- Embed the synchronizer process within the plugin runner
  ([#333](https://github.com/canvas-medical/canvas-plugins/pull/333),
  [`ab576f2`](https://github.com/canvas-medical/canvas-plugins/commit/ab576f2918a3a39530afa0dc8a81bbf6cc61c7cd))

### Chores

- Auto-update pre-commit hooks ([#268](https://github.com/canvas-medical/canvas-plugins/pull/268),
  [`2df702e`](https://github.com/canvas-medical/canvas-plugins/commit/2df702ec61c39437a8186564491417824d4d2e2c))

- Bump ipython from 8.31.0 to 8.32.0
  ([#385](https://github.com/canvas-medical/canvas-plugins/pull/385),
  [`c47ab8a`](https://github.com/canvas-medical/canvas-plugins/commit/c47ab8a2e0a4f27b40eb3780949fb42a65fca3fa))

- Bump pytest-asyncio from 0.25.2 to 0.25.3 in the development-patches group
  ([#384](https://github.com/canvas-medical/canvas-plugins/pull/384),
  [`78e3d12`](https://github.com/canvas-medical/canvas-plugins/commit/78e3d1272d9fec9947b8fa607e5f673bd77e8863))

- Bump rapidfuzz from 3.11.0 to 3.12.1
  ([#379](https://github.com/canvas-medical/canvas-plugins/pull/379),
  [`0bc2b0a`](https://github.com/canvas-medical/canvas-plugins/commit/0bc2b0a71c14f3a4fbc169b24deea491bb97a261))

- Bump the development-minors group across 1 directory with 2 updates
  ([#383](https://github.com/canvas-medical/canvas-plugins/pull/383),
  [`b01f109`](https://github.com/canvas-medical/canvas-plugins/commit/b01f1093cf8f9a07c57bbd99b0728a284d19cc59))

- Proper fix integration tests ([#375](https://github.com/canvas-medical/canvas-plugins/pull/375),
  [`0563dc2`](https://github.com/canvas-medical/canvas-plugins/commit/0563dc205751fe0df108d2a506ab4be38dfb8434))

### Features

- Migrate from poetry to uv ([#355](https://github.com/canvas-medical/canvas-plugins/pull/355),
  [`268decd`](https://github.com/canvas-medical/canvas-plugins/commit/268decd3d1ca001afe6016a365953fe1aeb222c7))


## v0.16.0 (2025-01-29)

### Bug Fixes

- Add missing properties to note type
  ([#374](https://github.com/canvas-medical/canvas-plugins/pull/374),
  [`5da4d69`](https://github.com/canvas-medical/canvas-plugins/commit/5da4d6911576a180d7ac88714911e493673cf649))

### Chores

- Bump jinja2 from 3.1.4 to 3.1.5
  ([#282](https://github.com/canvas-medical/canvas-plugins/pull/282),
  [`3384f95`](https://github.com/canvas-medical/canvas-plugins/commit/3384f95830f8322f3886c4966ae8acf8feab7059))

- Bump pydantic from 2.10.5 to 2.10.6 in the production-patches group
  ([#358](https://github.com/canvas-medical/canvas-plugins/pull/358),
  [`aad30df`](https://github.com/canvas-medical/canvas-plugins/commit/aad30df8f83ed0699dc5b7d78322d01411dd919d))

- Bump restrictedpython from 7.4 to 8.0
  ([#352](https://github.com/canvas-medical/canvas-plugins/pull/352),
  [`08adeba`](https://github.com/canvas-medical/canvas-plugins/commit/08adeba55643f7fc351165d5d6c1528d9d58cf10))

### Features

- Add appointment to data module ([#348](https://github.com/canvas-medical/canvas-plugins/pull/348),
  [`90613dc`](https://github.com/canvas-medical/canvas-plugins/commit/90613dcb1f1750845a76c2e9ec7ee7dfd9178425))

- Add events and effects for book appointments form and search results
  ([#322](https://github.com/canvas-medical/canvas-plugins/pull/322),
  [`1d435bd`](https://github.com/canvas-medical/canvas-plugins/commit/1d435bd89108f96262f184548b1cb28240256e06))

- Add mixins for CommittableQuerySet and PatientAssetQuerySet
  ([#211](https://github.com/canvas-medical/canvas-plugins/pull/211),
  [`4d8f609`](https://github.com/canvas-medical/canvas-plugins/commit/4d8f609074eaebbf194be180bad2f310111b1dc0))

- Additional patient-centric data module models
  ([#327](https://github.com/canvas-medical/canvas-plugins/pull/327),
  [`38ecd1b`](https://github.com/canvas-medical/canvas-plugins/commit/38ecd1be38a3667dc4215f5177184afcf9764517))

- Adds DetectedIssueEvidence events and id field
  ([#303](https://github.com/canvas-medical/canvas-plugins/pull/303),
  [`080006f`](https://github.com/canvas-medical/canvas-plugins/commit/080006feed68e88ec86b631c4f13b85ed2cc70a5))

- Allow html to be used in LaunchModalEffect
  ([#306](https://github.com/canvas-medical/canvas-plugins/pull/306),
  [`5976b59`](https://github.com/canvas-medical/canvas-plugins/commit/5976b59d39887e2f78ae9bee5e34d811d4039e69))

- Change the Command model to use a foreign key to Note
  ([#278](https://github.com/canvas-medical/canvas-plugins/pull/278),
  [`c887a8e`](https://github.com/canvas-medical/canvas-plugins/commit/c887a8e65b0605302bbdcfb57a3d54e78eaaebd2))

- Initial additions for Problem List Hygiene protocol conversion
  ([#230](https://github.com/canvas-medical/canvas-plugins/pull/230),
  [`114fd22`](https://github.com/canvas-medical/canvas-plugins/commit/114fd22393adbb747f451480176d689295394c39))


## v0.15.0 (2025-01-28)

### Bug Fixes

- Reloading relative imports on plugin updates
  ([#323](https://github.com/canvas-medical/canvas-plugins/pull/323),
  [`42f34f8`](https://github.com/canvas-medical/canvas-plugins/commit/42f34f826953f1014314d4752369e2cd0df073e8))

### Chores

- Bump the production-patches group across 1 directory with 3 updates
  ([#334](https://github.com/canvas-medical/canvas-plugins/pull/334),
  [`38149ad`](https://github.com/canvas-medical/canvas-plugins/commit/38149ada89c8d93eceea3dcf309ddf25ada00e41))

- Ensure test plugins are unloaded between tests
  ([#337](https://github.com/canvas-medical/canvas-plugins/pull/337),
  [`9fafe24`](https://github.com/canvas-medical/canvas-plugins/commit/9fafe24af98e2ad6b0f7a1abe2046729a278510a))

- Fix integration tests ([#367](https://github.com/canvas-medical/canvas-plugins/pull/367),
  [`3d15c2f`](https://github.com/canvas-medical/canvas-plugins/commit/3d15c2fd7849ee787a24a6badf8443100315eed3))

- Fix python warnings ([#335](https://github.com/canvas-medical/canvas-plugins/pull/335),
  [`22f83ff`](https://github.com/canvas-medical/canvas-plugins/commit/22f83ffd9ebe395bf6bd5372d8bf1c1ea76626e1))

### Features

- Add additional allowed imports ([#350](https://github.com/canvas-medical/canvas-plugins/pull/350),
  [`518c62c`](https://github.com/canvas-medical/canvas-plugins/commit/518c62cddd1355297507532e491916d436598917))

- Add cancel and reschedule appointment events
  ([#305](https://github.com/canvas-medical/canvas-plugins/pull/305),
  [`812e977`](https://github.com/canvas-medical/canvas-plugins/commit/812e977610e1d51464dd2dc29676ca328710bac6))

Co-authored-by: Miguel Quintas <miguelquintas@Mac.lan>

- Add events and effects for patient portal appointments actions
  ([#308](https://github.com/canvas-medical/canvas-plugins/pull/308),
  [`0f1359a`](https://github.com/canvas-medical/canvas-plugins/commit/0f1359ad58bd7b8a9519832b49818d0897ec007b))

Co-authored-by: Miguel Quintas <miguelquintas@Miguels-MacBook-Pro.local>

Co-authored-by: Nuno Silva <nuno.silva@canvasmedical.com>

### Refactoring

- Set up v1 of the data module as a Django application such that v2 can be added later
  ([#319](https://github.com/canvas-medical/canvas-plugins/pull/319),
  [`b5276d7`](https://github.com/canvas-medical/canvas-plugins/commit/b5276d74905bc4f83d6f62f8911a98173013afa2))

### Testing

- Use `raise_for_status()` when making http requests in integration tests
  ([#364](https://github.com/canvas-medical/canvas-plugins/pull/364),
  [`df947cc`](https://github.com/canvas-medical/canvas-plugins/commit/df947ccc21dcddc9c84bf8ab6854a54c68480772))


## v0.14.0 (2025-01-15)

### Bug Fixes

- Remove boto3 ([#314](https://github.com/canvas-medical/canvas-plugins/pull/314),
  [`a0abdec`](https://github.com/canvas-medical/canvas-plugins/commit/a0abdec96efbf779bf2831d53d5bdf5f0222e287))

### Features

- Added new CreateQuestionnaireResult effect type
  ([#250](https://github.com/canvas-medical/canvas-plugins/pull/250),
  [`5a1b5bb`](https://github.com/canvas-medical/canvas-plugins/commit/5a1b5bb66705d0ba0918def2578cd47ab1dcf60f))

Signed-off-by: Christopher Sande <christopher.sande@canvasmedical.com>

Co-authored-by: Reba Magier <reba.magier@canvasmedical.com>


## v0.13.3 (2025-01-14)

### Bug Fixes

- Send sighup after installing when synchronizer boots, remove load com…
  ([#324](https://github.com/canvas-medical/canvas-plugins/pull/324),
  [`bd82819`](https://github.com/canvas-medical/canvas-plugins/commit/bd82819f31d2948a85ba7ee8e6dab4d1021b02ba))

- Set null=True for all ForeignKey fields
  ([#301](https://github.com/canvas-medical/canvas-plugins/pull/301),
  [`5c4be8f`](https://github.com/canvas-medical/canvas-plugins/commit/5c4be8fea7ddf859c5bcb91d7ac709928153c7e2))


## v0.13.2 (2025-01-10)

### Bug Fixes

- Provide a default for CUSTOMER_IDENTIFIER
  ([#312](https://github.com/canvas-medical/canvas-plugins/pull/312),
  [`7d713c3`](https://github.com/canvas-medical/canvas-plugins/commit/7d713c36892c91237ba4a9fd863253b84a1980a3))


## v0.13.1 (2025-01-09)

### Bug Fixes

- Force build
  ([`8907f28`](https://github.com/canvas-medical/canvas-plugins/commit/8907f289712522f17d200f38f89390346a4cf58a))

### Refactoring

- A new implementation of the plugin installer that runs in the plugin
  ([#283](https://github.com/canvas-medical/canvas-plugins/pull/283),
  [`219f54e`](https://github.com/canvas-medical/canvas-plugins/commit/219f54e55a986627ddb92471c290facd3836dac9))

Co-authored-by: semantic-release <semantic-release>

Co-authored-by: Beau Gunderson <beau@beaugunderson.com>


## v0.13.0 (2025-01-07)

### Features

- Install applications via plugins
  ([#275](https://github.com/canvas-medical/canvas-plugins/pull/275),
  [`d0a5f59`](https://github.com/canvas-medical/canvas-plugins/commit/d0a5f59643785732f3f9dae5b2982fa1244604e5))


## v0.12.0 (2025-01-06)

### Features

- Add note action buttons events and effects
  ([#258](https://github.com/canvas-medical/canvas-plugins/pull/258),
  [`54b8008`](https://github.com/canvas-medical/canvas-plugins/commit/54b800842a495475b5f86af78fb8552d2a469ee8))

- Add ROS, SA and physical Exam commands and Practice Location and Org to data module
  ([#257](https://github.com/canvas-medical/canvas-plugins/pull/257),
  [`8e75918`](https://github.com/canvas-medical/canvas-plugins/commit/8e759187861d6860a18de17baf24c0a6caded19d))

Co-authored-by: Joe Wilson <joe.wilson@canvasmedical.com>

- Events and effects for patient portal intake forms
  ([#277](https://github.com/canvas-medical/canvas-plugins/pull/277),
  [`4f68da8`](https://github.com/canvas-medical/canvas-plugins/commit/4f68da8d6a4393ec5f9d9264a83e8e03214a4ed9))


## v0.11.1 (2025-01-02)

### Bug Fixes

- Deprecation warning message for BaseHandler event target
  ([#295](https://github.com/canvas-medical/canvas-plugins/pull/295),
  [`f20a790`](https://github.com/canvas-medical/canvas-plugins/commit/f20a7902952cd8d60ed6fdf9d75803d70b116ac4))


## v0.11.0 (2025-01-02)

### Chores

- Targeting python 3.12 in CI ([#281](https://github.com/canvas-medical/canvas-plugins/pull/281),
  [`c2ec60c`](https://github.com/canvas-medical/canvas-plugins/commit/c2ec60ce753e78ef9a5a40ede60ad4ebcce94da3))

### Features

- Adds surescripts effect types and classes
  ([#246](https://github.com/canvas-medical/canvas-plugins/pull/246),
  [`500f38f`](https://github.com/canvas-medical/canvas-plugins/commit/500f38f14e824271170c785222649cc652033a56))

- Refactor ProtocolBaseHandler and add target_type to Events
  ([#236](https://github.com/canvas-medical/canvas-plugins/pull/236),
  [`d90dcd8`](https://github.com/canvas-medical/canvas-plugins/commit/d90dcd87f5329f49018d1802e4229c6698de7555))


## v0.10.2 (2024-12-21)

### Bug Fixes

- Ignore hidden folders, hidden files and symlinks when building a plugin package
  ([#242](https://github.com/canvas-medical/canvas-plugins/pull/242),
  [`cbd96fa`](https://github.com/canvas-medical/canvas-plugins/commit/cbd96fa024f126fe99f93a528d590c8eae71c401))

- Improve error handling for canvas_cli install
  ([#267](https://github.com/canvas-medical/canvas-plugins/pull/267),
  [`7b8caf6`](https://github.com/canvas-medical/canvas-plugins/commit/7b8caf63c3308eeff1d0a7b3fdd5eba2e00e380a))

- Improve error handling for canvas_cli install command
  ([#241](https://github.com/canvas-medical/canvas-plugins/pull/241),
  [`2c3c749`](https://github.com/canvas-medical/canvas-plugins/commit/2c3c749d4d68fb7e4a01d8a9a857c28519d513ad))

- Upgrade Python to 3.12 to match GitHub's runners
  ([`9d42b25`](https://github.com/canvas-medical/canvas-plugins/commit/9d42b25d5b8e85d3bf430702b2896f866f535d2f))

### Chores

- Auto-update pre-commit hooks ([#231](https://github.com/canvas-medical/canvas-plugins/pull/231),
  [`ffc2a76`](https://github.com/canvas-medical/canvas-plugins/commit/ffc2a761d48e3d87dca9677719635cc5f36ae68a))

- Bump ipython from 8.29.0 to 8.30.0
  ([#255](https://github.com/canvas-medical/canvas-plugins/pull/255),
  [`5dbdc3d`](https://github.com/canvas-medical/canvas-plugins/commit/5dbdc3dbb05481ac53832197a78745e782de831b))

- Bump protobuf from 4.25.5 to 5.29.1
  ([#228](https://github.com/canvas-medical/canvas-plugins/pull/228),
  [`3b5c69b`](https://github.com/canvas-medical/canvas-plugins/commit/3b5c69bf4b5a6ed00b8e5733cf520eedb4be4cd7))

- Bump pydantic from 2.9.2 to 2.10.3
  ([#227](https://github.com/canvas-medical/canvas-plugins/pull/227),
  [`1ecb6e2`](https://github.com/canvas-medical/canvas-plugins/commit/1ecb6e2dcb0169d63aaafe272758bb6280f59ee3))

- Bump the development-minors group with 3 updates
  ([#254](https://github.com/canvas-medical/canvas-plugins/pull/254),
  [`55ea34b`](https://github.com/canvas-medical/canvas-plugins/commit/55ea34bb599a44f3cb237d8da4d8061750f5abff))

- Bump the development-patches group with 2 updates
  ([#253](https://github.com/canvas-medical/canvas-plugins/pull/253),
  [`7d0cc70`](https://github.com/canvas-medical/canvas-plugins/commit/7d0cc70122d182cc2f2ac63145e6a13f30b81c7e))

- Bump the production-patches group across 1 directory with 4 updates
  ([#235](https://github.com/canvas-medical/canvas-plugins/pull/235),
  [`768baf5`](https://github.com/canvas-medical/canvas-plugins/commit/768baf53567d786b86f5c8cd24fa4d46280fa70c))

- Bump typer from 0.13.1 to 0.15.1
  ([#256](https://github.com/canvas-medical/canvas-plugins/pull/256),
  [`561a226`](https://github.com/canvas-medical/canvas-plugins/commit/561a226b0e8bb7cf989ce1c23aa8245aeda09ecf))


## v0.10.1 (2024-12-12)

### Bug Fixes

- Typeddict import on patient configuration effect
  ([#249](https://github.com/canvas-medical/canvas-plugins/pull/249),
  [`d0069b8`](https://github.com/canvas-medical/canvas-plugins/commit/d0069b868894e9016644d28649dec5a1f34664be))


## v0.10.0 (2024-12-10)

### Bug Fixes

- Remove a warning that happens at install time
  ([#232](https://github.com/canvas-medical/canvas-plugins/pull/232),
  [`331eaa4`](https://github.com/canvas-medical/canvas-plugins/commit/331eaa494e67ebddb5ab61ee3f63546c4986045c))

### Features

- Add events and effects for preferred pharmacies search
  ([#220](https://github.com/canvas-medical/canvas-plugins/pull/220),
  [`f9c41b8`](https://github.com/canvas-medical/canvas-plugins/commit/f9c41b84421896afab79d08f1176abdddca305b7))

- Add patient profile section event and effect
  ([#212](https://github.com/canvas-medical/canvas-plugins/pull/212),
  [`f784d8f`](https://github.com/canvas-medical/canvas-plugins/commit/f784d8fa69244142685f2420bc3f6d0416bdd3e8))


## v0.9.0 (2024-12-05)

### Features

- Requirements for CKD CQM plugin
  ([#194](https://github.com/canvas-medical/canvas-plugins/pull/194),
  [`ed64c73`](https://github.com/canvas-medical/canvas-plugins/commit/ed64c73a6e54c4e0939cae60bf35e96212518395))

Signed-off-by: Christopher Sande <christopher.sande@canvasmedical.com>


## v0.8.2 (2024-12-05)

### Bug Fixes

- Plugin uploading was trying to use UTF-8
  ([`c4d641f`](https://github.com/canvas-medical/canvas-plugins/commit/c4d641f647801f64a8e9009e47a9842614dc4715))


## v0.8.1 (2024-12-04)

### Bug Fixes

- Update dependencies for Python 3.12 support
  ([#226](https://github.com/canvas-medical/canvas-plugins/pull/226),
  [`42b795e`](https://github.com/canvas-medical/canvas-plugins/commit/42b795e80e64e50efaf6470160d89da06cb1fb68))

### Chores

- Auto-update pre-commit hooks ([#200](https://github.com/canvas-medical/canvas-plugins/pull/200),
  [`c422a3f`](https://github.com/canvas-medical/canvas-plugins/commit/c422a3fda7f5bda5c1623c97f1afd40ef793596c))

- Consolidate linters and formatter into Ruff for improved performance and simplicity
  ([#216](https://github.com/canvas-medical/canvas-plugins/pull/216),
  [`15d2809`](https://github.com/canvas-medical/canvas-plugins/commit/15d2809339da704976213cbe448e7221120422de))

- Update dependencies for Python 3.12 support
  ([#226](https://github.com/canvas-medical/canvas-plugins/pull/226),
  [`d637bc6`](https://github.com/canvas-medical/canvas-plugins/commit/d637bc661e576ba550f57e76a9428fc8456b0522))


## v0.8.0 (2024-12-03)

### Features

- Add POST_COMMAND_INSERTED_INTO_NOTE event
  ([#222](https://github.com/canvas-medical/canvas-plugins/pull/222),
  [`da964eb`](https://github.com/canvas-medical/canvas-plugins/commit/da964eb3982d5d06f016534e0352597fa777bc02))


## v0.7.1 (2024-11-26)

### Bug Fixes

- Fixes inheritance issue ([#210](https://github.com/canvas-medical/canvas-plugins/pull/210),
  [`d5d0ac1`](https://github.com/canvas-medical/canvas-plugins/commit/d5d0ac15301e78a3004471dd47a8e409b26b7361))


## v0.7.0 (2024-11-26)

### Chores

- Update env-tools to support Python 3.12+
  ([#207](https://github.com/canvas-medical/canvas-plugins/pull/207),
  [`b3578ca`](https://github.com/canvas-medical/canvas-plugins/commit/b3578ca882a53f0ed1e94f2f15b9c20621ddcfcc))

### Features

- Add models for task, task labels, task comments and staff
  ([#202](https://github.com/canvas-medical/canvas-plugins/pull/202),
  [`0fc5590`](https://github.com/canvas-medical/canvas-plugins/commit/0fc55901111d770bad6de5d1f6bdc160c33d7b5c))

- Adds TASK_CLOSED and TASK_COMPLETED events
  ([#205](https://github.com/canvas-medical/canvas-plugins/pull/205),
  [`062786a`](https://github.com/canvas-medical/canvas-plugins/commit/062786aaa498b8cc9f5b4e4bd17c39d4d31bb039))

- Moves task effects ([#208](https://github.com/canvas-medical/canvas-plugins/pull/208),
  [`ea80d80`](https://github.com/canvas-medical/canvas-plugins/commit/ea80d804a36b0aab5249cf42670b2d773236b1aa))

- Plugins functionality for protocol conversions
  ([#183](https://github.com/canvas-medical/canvas-plugins/pull/183),
  [`69e95c8`](https://github.com/canvas-medical/canvas-plugins/commit/69e95c8894c051f06a9fd60e05704cbf24edf48a))

Signed-off-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com>

Co-authored-by: Christopher Sande <christopher.sande@canvasmedical.com>

Co-authored-by: José Magalhães <jose.magalhaes@canvasmedical.com>

Co-authored-by: Michela Iannaccone <mbiannaccone@gmail.com>

Co-authored-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com>


## v0.6.0 (2024-11-21)

### Bug Fixes

- Related name for ProtocolOverride
  ([#201](https://github.com/canvas-medical/canvas-plugins/pull/201),
  [`53fd89b`](https://github.com/canvas-medical/canvas-plugins/commit/53fd89b9759845a07f1af65f9dac39c0d0f917fd))

Signed-off-by: Christopher Sande <christopher.sande@canvasmedical.com>

### Features

- Add line_number option when originating command
  ([#171](https://github.com/canvas-medical/canvas-plugins/pull/171),
  [`791d446`](https://github.com/canvas-medical/canvas-plugins/commit/791d4462fe3fdfa41b8b1f6254c12f3c90f613a8))

- Add patient_filter to base effect's payload
  ([#192](https://github.com/canvas-medical/canvas-plugins/pull/192),
  [`1757447`](https://github.com/canvas-medical/canvas-plugins/commit/1757447b864e910f0567b8607546fa49c1afd858))


## v0.5.0 (2024-11-19)

### Bug Fixes

- Prevent plugin runner from exiting when loading a plugin with errors
  ([#190](https://github.com/canvas-medical/canvas-plugins/pull/190),
  [`beb6769`](https://github.com/canvas-medical/canvas-plugins/commit/beb67694a42e2a13f36452d69bda65745b3ad6d1))

### Chores

- Auto-update pre-commit hooks ([#198](https://github.com/canvas-medical/canvas-plugins/pull/198),
  [`a4046a7`](https://github.com/canvas-medical/canvas-plugins/commit/a4046a7a251061a9ead37c22ce53983530ebd8dd))

- Bump aiohttp from 3.10.5 to 3.10.11
  ([#197](https://github.com/canvas-medical/canvas-plugins/pull/197),
  [`cc2138a`](https://github.com/canvas-medical/canvas-plugins/commit/cc2138ac32b8691567d820263f5d0baa18cacd4d))

- Bump grpcio from 1.67.1 to 1.68.0
  ([#196](https://github.com/canvas-medical/canvas-plugins/pull/196),
  [`4980319`](https://github.com/canvas-medical/canvas-plugins/commit/498031977fd5a07d87ee83601b87ab35c6b79165))

- Bump pyjwt from 2.9.0 to 2.10.0
  ([#195](https://github.com/canvas-medical/canvas-plugins/pull/195),
  [`6417714`](https://github.com/canvas-medical/canvas-plugins/commit/641771461c230799e15737bc9dab7369d4e49d8c))

- Bump python-semantic-release from 9.12.1 to 9.14.0 in the development-minors group
  ([#189](https://github.com/canvas-medical/canvas-plugins/pull/189),
  [`bf236a7`](https://github.com/canvas-medical/canvas-plugins/commit/bf236a7b3fe75643dbcf9d14b0fc9d2cebf9bfdb))

- Bump typer from 0.12.5 to 0.13.0
  ([#185](https://github.com/canvas-medical/canvas-plugins/pull/185),
  [`170fdf8`](https://github.com/canvas-medical/canvas-plugins/commit/170fdf8408c03273dee802940add5a321c45cfa8))

- Bump typer from 0.13.0 to 0.13.1 in the production-patches group
  ([#199](https://github.com/canvas-medical/canvas-plugins/pull/199),
  [`93ddd99`](https://github.com/canvas-medical/canvas-plugins/commit/93ddd99ea0faa9760e0b4302ff321fded17625c6))

### Features

- Add capabilities for coding gap related plugins
  ([#191](https://github.com/canvas-medical/canvas-plugins/pull/191),
  [`45bf543`](https://github.com/canvas-medical/canvas-plugins/commit/45bf543e09bd53d4c8cb06f5cd522eae74e0dba7))

- Add coding gaps to patient chart configuration effect
  ([#186](https://github.com/canvas-medical/canvas-plugins/pull/186),
  [`a32bf18`](https://github.com/canvas-medical/canvas-plugins/commit/a32bf18f3f975621f3e2ba32834c2252e4509b46))

- Data module model for ProtocolOverride
  ([#149](https://github.com/canvas-medical/canvas-plugins/pull/149),
  [`0556717`](https://github.com/canvas-medical/canvas-plugins/commit/055671730410fc01110452346c5f6763db1d4aea))

Signed-off-by: Christopher Sande <csande@gmail.com>

- **plugins**: Add support for importing other modules within a plugin
  ([#180](https://github.com/canvas-medical/canvas-plugins/pull/180),
  [`ac077fe`](https://github.com/canvas-medical/canvas-plugins/commit/ac077fef42a7eefd985bcd93e4681ab3b019ce52))


## v0.4.0 (2024-11-12)

### Chores

- Bump django from 5.1.2 to 5.1.3 in the production-patches group
  ([#179](https://github.com/canvas-medical/canvas-plugins/pull/179),
  [`163540a`](https://github.com/canvas-medical/canvas-plugins/commit/163540a7b833e52f5fa50a17f595fda1e1adaa63))

- Bump the development-patches group across 1 directory with 2 updates
  ([#182](https://github.com/canvas-medical/canvas-plugins/pull/182),
  [`babb355`](https://github.com/canvas-medical/canvas-plugins/commit/babb3556ef487fb546319e526fca519ea6c6dbd8))

- Improve mypy configuration and fix the resulting errors
  ([#187](https://github.com/canvas-medical/canvas-plugins/pull/187),
  [`44071f1`](https://github.com/canvas-medical/canvas-plugins/commit/44071f13f069027d1d1fdadc932fe167010591ac))

### Code Style

- Use pathlib to construct a path
  ([#176](https://github.com/canvas-medical/canvas-plugins/pull/176),
  [`12e7c49`](https://github.com/canvas-medical/canvas-plugins/commit/12e7c49a04d25bf8767f856b53c1506870992349))

### Features

- Add is_predictive property to cqm class meta
  ([#181](https://github.com/canvas-medical/canvas-plugins/pull/181),
  [`9ff3117`](https://github.com/canvas-medical/canvas-plugins/commit/9ff3117a0758d17d7381e39721dcbdbc7ea12f12))

- Add plugin_created and plugin_updated events
  ([#178](https://github.com/canvas-medical/canvas-plugins/pull/178),
  [`efd45e2`](https://github.com/canvas-medical/canvas-plugins/commit/efd45e281e6d63ba0c8865e92e5521186df476b3))

- Adds imaging models ([#137](https://github.com/canvas-medical/canvas-plugins/pull/137),
  [`84c63e2`](https://github.com/canvas-medical/canvas-plugins/commit/84c63e2cb1225f1c481ea7b59d5fb2963afba08b))

- Adds more lab related models ([#130](https://github.com/canvas-medical/canvas-plugins/pull/130),
  [`6177e00`](https://github.com/canvas-medical/canvas-plugins/commit/6177e00a32f24e314c80aa6223249a341a745835))

Signed-off-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com>

Co-authored-by: Kristen ONeill <91080969+kristenoneill@users.noreply.github.com>


## v0.3.1 (2024-10-31)

### Bug Fixes

- Valueset query ([#175](https://github.com/canvas-medical/canvas-plugins/pull/175),
  [`3b4d7b5`](https://github.com/canvas-medical/canvas-plugins/commit/3b4d7b53c6a385ebd862d15cf8a3b8b0a7af0d36))

### Chores

- Fix test distribution step on semantic release gh action
  ([#173](https://github.com/canvas-medical/canvas-plugins/pull/173),
  [`6ee6b0c`](https://github.com/canvas-medical/canvas-plugins/commit/6ee6b0c715b771072a9a81b91bc7cc7f7bcb16e7))

- Local development improvements ([#102](https://github.com/canvas-medical/canvas-plugins/pull/102),
  [`ca4458e`](https://github.com/canvas-medical/canvas-plugins/commit/ca4458e59ee51abf638facb8eb9ff231be0efa18))

Co-authored-by: José Magalhães <jose.magalhaes@canvasmedical.com>


## v0.3.0 (2024-10-29)

### Bug Fixes

- Pull out meta properties of CQM protocols without importing file
  ([#140](https://github.com/canvas-medical/canvas-plugins/pull/140),
  [`1402f8e`](https://github.com/canvas-medical/canvas-plugins/commit/1402f8ea35107dbc0900dd6aad48cb5a0ac9aebd))

### Chores

- Add dependabot config ([#150](https://github.com/canvas-medical/canvas-plugins/pull/150),
  [`f8841fd`](https://github.com/canvas-medical/canvas-plugins/commit/f8841fdcae718da368a588c9630fa9844318aa5f))

- Auto-update pre-commit hooks ([#142](https://github.com/canvas-medical/canvas-plugins/pull/142),
  [`d4aff18`](https://github.com/canvas-medical/canvas-plugins/commit/d4aff18587a8802f0bd5fcf0f431586a533fd9f9))

- Auto-update pre-commit hooks ([#146](https://github.com/canvas-medical/canvas-plugins/pull/146),
  [`b0bfb46`](https://github.com/canvas-medical/canvas-plugins/commit/b0bfb46a14d5133894310641618fa3f97b45064e))

- Bump grpcio from 1.62.0 to 1.67.0
  ([#165](https://github.com/canvas-medical/canvas-plugins/pull/165),
  [`030048d`](https://github.com/canvas-medical/canvas-plugins/commit/030048df188566822e2ce0f6de4ea0e354aec0ce))

- Bump grpcio from 1.67.0 to 1.67.1 in the production-patches group
  ([#172](https://github.com/canvas-medical/canvas-plugins/pull/172),
  [`22c5bc3`](https://github.com/canvas-medical/canvas-plugins/commit/22c5bc33ac21b77e7b0854abeb5f2cc2dcb12ace))

- Bump grpcio-tools from 1.62.0 to 1.62.3 in the development-minors group
  ([#168](https://github.com/canvas-medical/canvas-plugins/pull/168),
  [`755f741`](https://github.com/canvas-medical/canvas-plugins/commit/755f741562b2bde3e69df44f85aeee1b90bd4290))

- Bump ipython from 8.21.0 to 8.29.0
  ([#159](https://github.com/canvas-medical/canvas-plugins/pull/159),
  [`54d2651`](https://github.com/canvas-medical/canvas-plugins/commit/54d265186e2cc679fdbc240dd7405964c594673c))

- Bump jsonschema from 4.21.1 to 4.23.0
  ([#163](https://github.com/canvas-medical/canvas-plugins/pull/163),
  [`5be8644`](https://github.com/canvas-medical/canvas-plugins/commit/5be8644a9a0befbcc7806be5b424164b51f366ad))

- Bump keyring from 24.3.0 to 25.4.1
  ([#157](https://github.com/canvas-medical/canvas-plugins/pull/157),
  [`23327a5`](https://github.com/canvas-medical/canvas-plugins/commit/23327a5cab5621e9471aa1f2f0871946e8a44921))

- Bump keyring from 25.4.1 to 25.5.0
  ([#170](https://github.com/canvas-medical/canvas-plugins/pull/170),
  [`c7ca11d`](https://github.com/canvas-medical/canvas-plugins/commit/c7ca11d5d262a2a1b4b9808ef0fef834b3523fd7))

- Bump peter-evans/create-pull-request from 4 to 7
  ([#151](https://github.com/canvas-medical/canvas-plugins/pull/151),
  [`47e6c8f`](https://github.com/canvas-medical/canvas-plugins/commit/47e6c8f96cb535f0aa81fd976a108e02d7c8182b))

- Bump pre-commit from 3.6.2 to 4.0.1 in the development-majors group
  ([#155](https://github.com/canvas-medical/canvas-plugins/pull/155),
  [`6eb777b`](https://github.com/canvas-medical/canvas-plugins/commit/6eb777b695edd79f291a763d5466a7b22316cf07))

- Bump pre-commit/action from 3.0.0 to 3.0.1
  ([#152](https://github.com/canvas-medical/canvas-plugins/pull/152),
  [`3bd3919`](https://github.com/canvas-medical/canvas-plugins/commit/3bd39191efcab214634fbb5b06440d45ff63c8cb))

- Bump protobuf from 4.25.3 to 4.25.5
  ([#156](https://github.com/canvas-medical/canvas-plugins/pull/156),
  [`85e23dd`](https://github.com/canvas-medical/canvas-plugins/commit/85e23dd61247ad1db45b82f4a8db48ddbabeae87))

- Bump pydantic from 2.6.1 to 2.9.2
  ([#164](https://github.com/canvas-medical/canvas-plugins/pull/164),
  [`14d4be1`](https://github.com/canvas-medical/canvas-plugins/commit/14d4be1ee7f4051eb7f7bb19bee15d5a7402674d))

- Bump pyjwt from 2.4.0 to 2.9.0 ([#167](https://github.com/canvas-medical/canvas-plugins/pull/167),
  [`594dc74`](https://github.com/canvas-medical/canvas-plugins/commit/594dc74ca88244307a6e43230ad9a75ec57dfc43))

- Bump redis from 5.0.4 to 5.2.0 ([#161](https://github.com/canvas-medical/canvas-plugins/pull/161),
  [`fe40619`](https://github.com/canvas-medical/canvas-plugins/commit/fe4061918e49173a7aecb8a7312f7f39e064005c))

- Bump restrictedpython from 7.3 to 7.4
  ([#166](https://github.com/canvas-medical/canvas-plugins/pull/166),
  [`1acb504`](https://github.com/canvas-medical/canvas-plugins/commit/1acb504469b0c6ae99f3ae3d2f41eacefeb3a80a))

- Bump the development-minors group with 8 updates
  ([#154](https://github.com/canvas-medical/canvas-plugins/pull/154),
  [`24b4d9a`](https://github.com/canvas-medical/canvas-plugins/commit/24b4d9aaee3209e60266caf973e2ac6a28369f09))

- Bump the production-patches group with 3 updates
  ([#153](https://github.com/canvas-medical/canvas-plugins/pull/153),
  [`9f3e69a`](https://github.com/canvas-medical/canvas-plugins/commit/9f3e69a79e46672a65830af3f0adac2703dc1191))

- Bump typer from 0.9.0 to 0.12.5
  ([#162](https://github.com/canvas-medical/canvas-plugins/pull/162),
  [`cb6af5c`](https://github.com/canvas-medical/canvas-plugins/commit/cb6af5c3a76a1326388604edd62e82186a0ee888))

- Bump typing-extensions from 4.8.0 to 4.12.2
  ([#158](https://github.com/canvas-medical/canvas-plugins/pull/158),
  [`47c4add`](https://github.com/canvas-medical/canvas-plugins/commit/47c4add0920124dabbdddff43bbb253cd15281d2))

- Bump websocket-client from 1.7.0 to 1.8.0
  ([#160](https://github.com/canvas-medical/canvas-plugins/pull/160),
  [`28b4389`](https://github.com/canvas-medical/canvas-plugins/commit/28b43891394312fd92af84d86e49f1a2095708a3))

- Clean up pre-commit-update workflow
  ([#141](https://github.com/canvas-medical/canvas-plugins/pull/141),
  [`2ab0694`](https://github.com/canvas-medical/canvas-plugins/commit/2ab0694215d6463e3e556dd76ae4f2dbc50e597f))

- Enhance release process by installing and executing the distribution
  ([#143](https://github.com/canvas-medical/canvas-plugins/pull/143),
  [`2d2352d`](https://github.com/canvas-medical/canvas-plugins/commit/2d2352d7354599a6bad15a7820a8c1d217144a6a))

- Fix pre-commit errors ([#138](https://github.com/canvas-medical/canvas-plugins/pull/138),
  [`1da3f33`](https://github.com/canvas-medical/canvas-plugins/commit/1da3f33adda53f73ec114075f1c581218f8e24ea))

- Improve generate-protobufs script
  ([#135](https://github.com/canvas-medical/canvas-plugins/pull/135),
  [`61597ab`](https://github.com/canvas-medical/canvas-plugins/commit/61597abea8cf16248c422657cbfa6632a056b396))

- **ci**: Fix pre-commit on CI ([#136](https://github.com/canvas-medical/canvas-plugins/pull/136),
  [`ec6b4b3`](https://github.com/canvas-medical/canvas-plugins/commit/ec6b4b3849582bdfcfea9cb605d894b62c9d1bf7))

### Features

- Add feedback_enabled property to protocol card effect
  ([#148](https://github.com/canvas-medical/canvas-plugins/pull/148),
  [`5dd7d96`](https://github.com/canvas-medical/canvas-plugins/commit/5dd7d963fd36a627c6072c8ead83e76eaa8ad950))

- Add more event types ([#139](https://github.com/canvas-medical/canvas-plugins/pull/139),
  [`ffc9c25`](https://github.com/canvas-medical/canvas-plugins/commit/ffc9c255181da5a95a0bd4e1535c988e40e39761))

- Add protocol classname to effects and include in plugin_runner event handler
  ([#145](https://github.com/canvas-medical/canvas-plugins/pull/145),
  [`517cadb`](https://github.com/canvas-medical/canvas-plugins/commit/517cadb18fc09ded585b74975edc74283acb7040))

- Add SDK Questionnaire and Interview models
  ([#104](https://github.com/canvas-medical/canvas-plugins/pull/104),
  [`ba8b556`](https://github.com/canvas-medical/canvas-plugins/commit/ba8b556ee1b36a173ab07ddd4d705d5b131c6fc7))

- Clipboard command events ([#147](https://github.com/canvas-medical/canvas-plugins/pull/147),
  [`eaf339a`](https://github.com/canvas-medical/canvas-plugins/commit/eaf339a1656978b04c16e4453d96c77c9ca868df))


## v0.2.11 (2024-10-15)

### Bug Fixes

- Fix settings error in canvas-cli
  ([#133](https://github.com/canvas-medical/canvas-plugins/pull/133),
  [`52e4438`](https://github.com/canvas-medical/canvas-plugins/commit/52e4438d57627b2e397ab2b2085e0a5579741f55))

* Adds settings to pyproject.toml.

* Adds .py extension to settings in pyproject.toml.

### Chores

- Fix semantic release workflow ([#134](https://github.com/canvas-medical/canvas-plugins/pull/134),
  [`97a5069`](https://github.com/canvas-medical/canvas-plugins/commit/97a5069d8eeda5c8f455c531feb5c1a40e4fb487))

- Fix semantic-release publish ([#129](https://github.com/canvas-medical/canvas-plugins/pull/129),
  [`8a24339`](https://github.com/canvas-medical/canvas-plugins/commit/8a24339455bb58246c78d2670b02465207991a4f))

- **docs**: Add CONTRIBUTING.md and CODE_OF_CONDUCT.md
  ([#132](https://github.com/canvas-medical/canvas-plugins/pull/132),
  [`365751b`](https://github.com/canvas-medical/canvas-plugins/commit/365751b186d8d20454cf059b749f9ebdcd3ebd56))

chore(docs): add CONTRIBUTING and CODE_OF_CONDUCT


## v0.2.10 (2024-10-14)

### Bug Fixes

- Improvements to the TaskCommand definition
  ([`1dbc4ee`](https://github.com/canvas-medical/canvas-plugins/commit/1dbc4eec4b0a58f264035f55c296054cbb7638e8))

### Chores

- Add pull request title validator
  ([#126](https://github.com/canvas-medical/canvas-plugins/pull/126),
  [`194bf0b`](https://github.com/canvas-medical/canvas-plugins/commit/194bf0b56c5c036de853ed149a702eecf7ec3af5))

- Bump restrictedpython from 7.1 to 7.3
  ([#117](https://github.com/canvas-medical/canvas-plugins/pull/117),
  [`ad5ccea`](https://github.com/canvas-medical/canvas-plugins/commit/ad5ccead18b238d809a4d9082d4ae4a14a439956))

Bump restrictedpython from 7.1 to 7.3

Bumps [restrictedpython](https://github.com/zopefoundation/RestrictedPython) from 7.1 to 7.3. -
  [Changelog](https://github.com/zopefoundation/RestrictedPython/blob/master/CHANGES.rst) -
  [Commits](https://github.com/zopefoundation/RestrictedPython/compare/7.1...7.3)

--- updated-dependencies: - dependency-name: restrictedpython dependency-type: direct:production

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- Fix semantic release ([#128](https://github.com/canvas-medical/canvas-plugins/pull/128),
  [`d4bbcc7`](https://github.com/canvas-medical/canvas-plugins/commit/d4bbcc737f08cd528b09a71a23cc6deabc427d66))

- **ci**: Add automated releases using semantic release
  ([#127](https://github.com/canvas-medical/canvas-plugins/pull/127),
  [`2f830c8`](https://github.com/canvas-medical/canvas-plugins/commit/2f830c8cfb4436b34502d457456e97b487e9c122))

- **ci**: Improve build and test workflow
  ([#125](https://github.com/canvas-medical/canvas-plugins/pull/125),
  [`5c15020`](https://github.com/canvas-medical/canvas-plugins/commit/5c1502037c1448f700657091c21e92513270a6eb))


## v0.2.9 (2024-10-08)

### Bug Fixes

- Add MedicalHistoryCommand to __init__
  ([`0b91465`](https://github.com/canvas-medical/canvas-plugins/commit/0b91465ada1dbbb1d3038d2e4aec07d2b8f85362))

- Improve AllergyCommand definition
  ([`049c16d`](https://github.com/canvas-medical/canvas-plugins/commit/049c16dc00aba1c13726855c42f6de0797c2e49f))


## v0.2.8 (2024-10-02)


## v0.2.7 (2024-09-27)

### Features

- Add patient_chart_summary_configuration effect and new event to configure patient chart summary
  ([#94](https://github.com/canvas-medical/canvas-plugins/pull/94),
  [`f53f61e`](https://github.com/canvas-medical/canvas-plugins/commit/f53f61e6132276ba8a54f51005b4995b9246ff59))

* add patient_chart_summary_configuration effect and new event to configure patient chart summary

* regen protobufs after rebase


## v0.2.6 (2024-09-26)

### Chores

- Add black ad dev dependency
  ([`4799bae`](https://github.com/canvas-medical/canvas-plugins/commit/4799bae667f2e99f1c557050781d86a491797c7f))

- Update protobufs
  ([`549adaa`](https://github.com/canvas-medical/canvas-plugins/commit/549adaaef8a466e41d7be8e470ef1b9d015b0df9))

### Features

- Add Allergy command SDK definition
  ([`87f05cf`](https://github.com/canvas-medical/canvas-plugins/commit/87f05cf16813e267b9cba7c8c947cee171dd44fd))

- Add CloseGoal command SDK definition
  ([`f99b86d`](https://github.com/canvas-medical/canvas-plugins/commit/f99b86d78498dcf16d04861d6674094b943c8165))

- Add effects for Perform Command
  ([`b379a28`](https://github.com/canvas-medical/canvas-plugins/commit/b379a289ac483ed1dcc1463b20bb7671aa43ba11))

- Add FamilyHistory command SDK definition
  ([`a77fa6d`](https://github.com/canvas-medical/canvas-plugins/commit/a77fa6dcb6f742827955da8c9afa7c1a83636480))

- Add instruct and perform commands
  ([`08997ed`](https://github.com/canvas-medical/canvas-plugins/commit/08997ed5f96bb2971eeed9a179704ffacaab6494))

- Add LabOrder command SDK definition
  ([`3348685`](https://github.com/canvas-medical/canvas-plugins/commit/3348685fb28ad9ea010e26c56550e10d545cf53f))

- Add MedicationHistory command SDK definition
  ([`e64238d`](https://github.com/canvas-medical/canvas-plugins/commit/e64238d7e1b8f54ccf43ff78248620497cb329b7))

- Add PastSurgicalHistory command SDK definition
  ([`332f898`](https://github.com/canvas-medical/canvas-plugins/commit/332f898fccb7422a495cf1914e5a301ed763a946))

- Add Refill command SDK definition
  ([`36b3e1e`](https://github.com/canvas-medical/canvas-plugins/commit/36b3e1e6c259562fa66e9e3ddfdc1c138a087e75))

- Add Task command SDK definition
  ([`4944078`](https://github.com/canvas-medical/canvas-plugins/commit/49440781416d56c8769b2e83ce78bd616e6b6f1a))

- Add UpdateDiagnosis command SDK definition
  ([`f751d07`](https://github.com/canvas-medical/canvas-plugins/commit/f751d074a4758a704c3de2ee4ba69470daf18f0b))

- Add Vitals command SDK definition
  ([`ad56f11`](https://github.com/canvas-medical/canvas-plugins/commit/ad56f1193d58e73b9cf5aef81e9c5787b8879a8e))

- Feat: add RemoveAllergy command SDK definition
  ([`40fa8d3`](https://github.com/canvas-medical/canvas-plugins/commit/40fa8d3afdb5e2beecac545dfe513dfec24cb6a0))


## v0.2.5 (2024-09-09)


## v0.2.4 (2024-09-04)


## v0.2.3 (2024-09-04)


## v0.2.2 (2024-09-03)


## v0.2.0 (2024-09-03)


## v0.1.15 (2024-07-25)


## v0.1.14 (2024-07-17)


## v0.1.13 (2024-07-03)


## v0.1.12 (2024-06-17)


## v0.1.11 (2024-06-12)


## v0.1.10 (2024-05-31)


## v0.1.9 (2024-05-31)


## v0.1.7 (2024-05-17)


## v0.0.7 (2024-05-16)


## v0.0.6 (2024-05-14)


## v0.0.5 (2024-05-13)


## v0.0.4 (2024-05-13)


## v0.0.3 (2024-04-03)


## v0.0.2 (2024-02-23)


## v0.0.1 (2024-02-21)
