# TODO
# - handle looking up implicit directory dependencies
#   http://git.pld-linux.org/?p=packages/rpm-whiteout.git;a=commitdiff;h=41210229710e3417017c97297e4b9d7278d4c415
#   http://git.pld-linux.org/?p=packages/systemd.git;a=commitdiff;h=60c3e1b7a372cc929a0ef70da372504584b92623
#   http://git.pld-linux.org/?p=packages/polkit.git;a=commitdiff;h=368d6c5e9e16354ce89a7fd940bacf78c9b0a90f
#
# Conditional build:
%bcond_without	tests		# build without tests

# TODO
# - PLDize (or drop) /etc/yum/version-groups.conf
%define	rpm_ver 5.4.10-50
Summary:	RPM installer/updater
Summary(pl.UTF-8):	Narzędzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	3.4.3
Release:	9
License:	GPL v2+
Group:		Applications/System
Source0:	http://yum.baseurl.org/download/3.4/%{name}-%{version}.tar.gz
# Source0-md5:	7c8ea8beba5b4e7fe0c215e4ebaa26ed
Source1:	%{name}-pld-source.repo
Source2:	%{name}-pld-ti-source.repo
# from util-vserver-*/contrib/
#Patch:		%{name}-chroot.patch # disabled for now. broken or not needed
Patch1:		%{name}-obsoletes.patch
Patch2:		cli-pyc.patch
Patch3:		%{name}-pld.patch
Patch4:		%{name}-amd64.patch
Patch5:		%{name}-config.patch
Patch6:		nosetests.patch
Patch7:		rpm5.patch
Patch8:		tests.patch
Patch9:		pld-release.patch
Patch10:	rpm5-%{name}.patch
Patch11:	rpm5-caps.patch
Patch12:	%{name}-missingok.patch
Patch13:	%{name}-info-no-size.patch
Patch14:	%{name}-pkgspec-at.patch
Patch15:	emptyfields.patch
# fc
Patch100:	%{name}-HEAD.patch
# Patch100-md5:	f53a297818b71da862eed4b7401e008e
Patch101:	installonlyn-enable.patch
Patch102:	%{name}-manpage-files.patch
Patch103:	no-more-exactarchlist.patch
Patch104:	%{name}-completion-helper.patch
Patch105:	%{name}-distro-configs.patch
URL:		http://yum.baseurl.org/
BuildRequires:	bash-completion >= 2.0
BuildRequires:	gettext-tools
BuildRequires:	intltool
BuildRequires:	python-rpm >= %{rpm_ver}
BuildRequires:	python-urlgrabber
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
BuildConflicts:	yum < 3.4.3-2.1
%if %{with tests}
BuildRequires:	python-nose
BuildRequires:	yum-metadata-parser
%if %(locale -a | grep -qFx en_US.utf8; echo $?)
BuildRequires:	glibc-localedb-all
%endif
%endif
Requires:	python >= 1:2.5
Requires:	python-iniparse
Requires:	python-libxml2
Requires:	python-pygpgme
Requires:	python-rpm >= %{rpm_ver}
Requires:	python-sqlite
Requires:	python-urlgrabber >= 1:3.9.1
Requires:	rpm >= %{rpm_ver}
Requires:	yum-metadata-parser >= 1.1.4
Obsoletes:	yum-plugin-security < 1.1.32
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		%{_prefix}/lib

%description
Yum is a utility that can check for and automatically download and
install updated RPM packages. Dependencies are obtained and downloaded
automatically prompting the user as necessary.

%description -l pl.UTF-8
Yum to narzędzie sprawdzające i automatycznie ściągające i instalujące
uaktualnione pakiety RPM. Zależności są ściągane automatycznie po
zapytaniu użytkownika w razie potrzeby.

%package -n bash-completion-%{name}
Summary:	bash-completion for Yum
Summary(pl.UTF-8):	Bashowe uzupełnianie parametrów dla Yuma
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 2.0

%description -n bash-completion-%{name}
bash-completion for Yum.

%description -n bash-completion-%{name} -l pl.UTF-8
Bashowe uzupełnianie parametrów dla Yuma.

%prep
%setup -q
# fc
%patch -P100 -p1
%patch -P101 -p0
%patch -P102 -p1
%patch -P103 -p1
%patch -P104 -p1
%patch -P105 -p1
# pld
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1
%patch -P8 -p1
%patch -P9 -p1
%patch -P10 -p1
%patch -P11 -p1
%patch -P12 -p1
%patch -P13 -p1
%patch -P14 -p1
%patch -P15 -p1

%build
%{__make}

%if %{with tests}
# yum itself must work (tests does not cover import errors)
# we ignore exit code, as it will exit with error if yum is not installed:
# $ ./yummain.py --version
#3.4.3
#CRITICAL:yum.cli:Config Error: Error accessing file for config file:///etc/yum.conf
# and it will fail other ways if incompatible yum version is installed

ver=$(./yummain.py --version | head -n1)
test $ver = %{version}

# test/check-po-yes-no.py prints chinese to screen, need to enable utf8
export LC_ALL=en_US.utf8
%{__make} test \
	NOSETESTS=nosetests-%{py_ver}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/yum/pluginconf.d,%{_libdir}/yum-plugins,%{_datadir}/yum-plugins}

%{__make} install -j1 \
	INIT=systemd \
	UNITDIR=%{systemdunitdir} \
	PYLIBDIR=%{py_scriptdir} \
	DESTDIR=$RPM_BUILD_ROOT

# no cron (unstable, and poldek is main pkg manager)
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/yum-cron.8*
%{__rm} $RPM_BUILD_ROOT%{_sbindir}/yum-cron
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/yum/yum-cron-hourly.conf
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/yum/yum-cron-security.conf
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/yum/yum-cron.conf
%{__rm} $RPM_BUILD_ROOT%{systemdunitdir}/yum-cron.service
%{__rm} $RPM_BUILD_ROOT/etc/cron.daily/0yum-daily.cron
%{__rm} $RPM_BUILD_ROOT/etc/cron.daily/0yum-security.cron
%{__rm} $RPM_BUILD_ROOT/etc/cron.hourly/0yum-hourly.cron

# for now, move repodir/yum.conf back
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/{yum/repos.d,/yum.repos.d}
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/{yum/yum.conf,yum.conf}

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/pld.repo

install -d $RPM_BUILD_ROOT/var/lib/yum/{history,plugins,yumdb}
# see yum.conf(5)
touch $RPM_BUILD_ROOT/var/lib/yum/uuid

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir} $RPM_BUILD_ROOT%{_datadir}/yum-cli
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir} $RPM_BUILD_ROOT%{_datadir}/yum-cli

%py_postclean %{_datadir}/yum-cli

%{__mv} $RPM_BUILD_ROOT%{_localedir}/lt{_LT,}
# duplicate with id, nl and pt
%{__rm} -r $RPM_BUILD_ROOT%{_localedir}/{id_ID,nl_NL,pt_PT}

%find_lang %{name}

# in yum-updatesd.spec
%{__rm} $RPM_BUILD_ROOT/etc/dbus-1/system.d/yum-updatesd.conf
%{__rm} $RPM_BUILD_ROOT/etc/rc.d/init.d/yum-updatesd
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/yum/yum-updatesd.conf
%{__rm} $RPM_BUILD_ROOT%{_sbindir}/yum-updatesd
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man5/yum-updatesd.conf.5*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/yum-updatesd.8*

%clean
rm -rf $RPM_BUILD_ROOT

%pretrans
# migrate to new dir. having two dirs is really confusing
if [ -d %{_sysconfdir}/yum/repos.d ]; then
	echo >&2 "Migrating %{_sysconfdir}/yum/repos.d to %{_sysconfdir}/yum.repos.d"
	mkdir -p %{_sysconfdir}/yum.repos.d
	for a in %{_sysconfdir}/yum/repos.d/*; do
		if [ -f "$a" ]; then
			mv -vf $a %{_sysconfdir}/yum.repos.d/${a##*/}
		fi
	done
	rm -rf %{_sysconfdir}/yum/repos.d
fi

%triggerpostun -- %{name} < 3.2.12-3
if [ -f %{_sysconfdir}/yum/repos.d/pld-source.repo.rpmsave ]; then
	cp -f %{_sysconfdir}/yum/repos.d/pld.repo{,.rpmnew}
	mv -f %{_sysconfdir}/yum/repos.d/{pld-source.repo.rpmsave,pld.repo}
fi

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README AUTHORS TODO INSTALL ChangeLog
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}

# main yum config
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum.conf

%dir %{_sysconfdir}/yum
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/version-groups.conf

%dir %{_sysconfdir}/yum.repos.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum.repos.d/*.repo

%dir %{_sysconfdir}/yum/pluginconf.d
%dir %{_sysconfdir}/yum/protected.d
%dir %{_sysconfdir}/yum/vars

%attr(755,root,root) %{_bindir}/yum
%{_mandir}/man5/yum.conf.5*
%{_mandir}/man8/yum-shell.8*
%{_mandir}/man8/yum.8*

%dir %{_datadir}/yum-cli
%{_datadir}/yum-cli/*.py*

%{py_sitescriptdir}/yum
%{py_sitescriptdir}/rpmUtils

%dir %{_libdir}/yum-plugins
%dir %{_datadir}/yum-plugins

%dir /var/cache/yum

%dir /var/lib/yum
%dir /var/lib/yum/history
%dir /var/lib/yum/plugins
%dir /var/lib/yum/yumdb
%ghost /var/lib/yum/uuid

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/yum
%{bash_compdir}/yummain.py
