#
# Conditional build:
%bcond_without	tests		# build without tests

# TODO
# - PLDize (or drop) /etc/yum/version-groups.conf
Summary:	RPM installer/updater
Summary(pl.UTF-8):	Narzędzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	3.4.3
Release:	3
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
# fc
Patch10:	%{name}-HEAD.patch
# Patch10-md5:	fed00a3fcdb2ab0115bf8e1949309763
Patch11:	installonlyn-enable.patch
Patch12:	%{name}-manpage-files.patch
Patch13:	no-more-exactarchlist.patch
Patch14:	%{name}-completion-helper.patch
Patch15:	%{name}-distro-configs.patch
URL:		http://yum.baseurl.org/
BuildRequires:	bash-completion >= 2.0
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	python-rpm
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
Requires:	python-rpm
Requires:	python-sqlite
Requires:	python-urlgrabber >= 1:3.9.1
Requires:	rpm >= 4.4.2
Requires:	yum-metadata-parser >= 1.1.4
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
Group:		Applications/Shells
Requires:	%{name}
Requires:	bash-completion >= 2.0

%description -n bash-completion-%{name}
bash-completion for Yum.

%prep
%setup -q
# fc
%patch10 -p1
%patch11 -p0
%patch12 -p1
%patch13 -p0
%patch14 -p1
%patch15 -p1
# pld
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

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
%{__make} install \
	PYLIBDIR=%{py_scriptdir} \
	DESTDIR=$RPM_BUILD_ROOT

# no cron (unstable, and poldek is main pkg manager)
%{__rm} $RPM_BUILD_ROOT/etc/cron.daily/0yum-update.cron
%{__rm} $RPM_BUILD_ROOT%{systemdunitdir}/yum-cron.service
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/yum/yum-cron.conf
%{__rm} $RPM_BUILD_ROOT%{_sbindir}/yum-cron
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/yum-cron.8*

# for now, move repodir/yum.conf back
mv $RPM_BUILD_ROOT%{_sysconfdir}/{yum/repos.d,/yum.repos.d}
mv $RPM_BUILD_ROOT%{_sysconfdir}/{yum/yum.conf,yum.conf}

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/pld.repo

install -d $RPM_BUILD_ROOT/var/lib/yum/{history,plugins,yumdb}
# see yum.conf(5)
touch $RPM_BUILD_ROOT/var/lib/yum/uuid

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir} $RPM_BUILD_ROOT%{_datadir}/yum-cli
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir} $RPM_BUILD_ROOT%{_datadir}/yum-cli

%py_postclean %{_datadir}/yum-cli

mv $RPM_BUILD_ROOT%{_localedir}/lt{_LT,}
# duplicate with id, nl and pt
rm -r $RPM_BUILD_ROOT%{_localedir}/id_ID
rm -r $RPM_BUILD_ROOT%{_localedir}/nl_NL
rm -r $RPM_BUILD_ROOT%{_localedir}/pt_PT

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

%dir %{py_sitescriptdir}/yum
%dir %{_datadir}/yum-cli
%{_datadir}/yum-cli/*.py[co]

%{py_sitescriptdir}/yum/*.py[co]
%dir %{py_sitescriptdir}/rpmUtils
%{py_sitescriptdir}/rpmUtils/*.py[co]

%dir %{_libdir}/yum-plugins
%dir %{_datadir}/yum-plugins

%{_mandir}/man5/yum.conf.5*
%{_mandir}/man8/yum-shell.8*
%{_mandir}/man8/yum.8*

%dir /var/cache/yum

%dir /var/lib/yum
%dir /var/lib/yum/history
%dir /var/lib/yum/plugins
%dir /var/lib/yum/yumdb
%ghost /var/lib/yum/uuid

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{_datadir}/bash-completion/completions/yum
%{_datadir}/bash-completion/completions/yummain.py
