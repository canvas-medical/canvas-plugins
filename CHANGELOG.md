# CHANGELOG


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
