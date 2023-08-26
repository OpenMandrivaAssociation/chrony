# Build system issues prevent debugedit from finding the right files
%undefine _debugsource_packages

Name:		chrony
Version:	4.4
Release:	1
Summary:	An NTP client/server
Group:		System/Base
License:	GPLv2
URL:		http://chrony.tuxfamily.org
Source0:	http://download.tuxfamily.org/chrony/%{name}-%{version}.tar.gz
Source1:	chrony.conf
Source2:	chrony.keys
Source3:	chronyd.service
Source4:	chrony.helper
Source5:	chrony.logrotate
Source7:	chrony.nm-dispatcher
Source8:	chrony.dhclient
Source9:	chrony-wait.service
BuildRequires:	pkgconfig(libcap)
BuildRequires:	pkgconfig(libedit)
BuildRequires:	bison
BuildRequires:	texinfo
BuildRequires:  rpm-helper
Requires(pre):	shadow-utils
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
Requires(postun):	rpm-helper
Requires(preun):	rpm-helper

%description
A client/server for the Network Time Protocol, this program keeps your
computer's clock accurate. It was specially designed to support
systems with intermittent internet connections, but it also works well
in permanently connected environments. It can use also hardware reference
clocks, system real-time clock or manual input as time references.

%prep
%setup -q

%build
%serverbuild
export CFLAGS="$CFLAGS -pie -fpie"
export LDFLAGS="$LDFLAGS -Wl,-z,relro,-z,now"

%configure \
        --docdir=%{_docdir} \
        --with-sendmail=%{_sbindir}/sendmail

%make_build getdate all docs

%install
%make_install install-docs

rm -rf %{buildroot}%{_docdir}

mkdir -p %{buildroot}%{_sysconfdir}/{sysconfig,logrotate.d}
mkdir -p %{buildroot}%{_localstatedir}/{lib,log}/chrony
mkdir -p %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d
mkdir -p %{buildroot}%{_sysconfdir}/dhcp/dhclient.d
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_unitdir}/ntp-units.d

install -m 644 -p %{SOURCE1} %{buildroot}%{_sysconfdir}/chrony.conf
install -m 640 -p %{SOURCE2} %{buildroot}%{_sysconfdir}/chrony.keys
install -m 644 -p %{SOURCE3} %{buildroot}%{_unitdir}/chronyd.service
install -m 755 -p %{SOURCE4} %{buildroot}%{_libexecdir}/chrony-helper
install -m 644 -p %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/chrony
install -m 755 -p %{SOURCE7} %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/20-chrony
install -m 755 -p %{SOURCE8} %{buildroot}%{_sysconfdir}/dhcp/dhclient.d/chrony.sh
install -m 644 -p %{SOURCE9} %{buildroot}%{_unitdir}/chrony-wait.service

touch %{buildroot}%{_localstatedir}/lib/chrony/{drift,rtc}
echo 'chronyd.service' > %{buildroot}%{_unitdir}/ntp-units.d/50-chronyd.list

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /sbin/nologin

%triggerun -- chrony < 1.25
if /sbin/chkconfig --level 3 chronyd; then
        /bin/systemctl enable chronyd.service &> /dev/null
fi
:

%files
%doc COPYING NEWS README examples/*
%config(noreplace) %{_sysconfdir}/chrony.conf
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,chrony) %{_sysconfdir}/chrony.keys
%config(noreplace) %{_sysconfdir}/logrotate.d/chrony
%{_sysconfdir}/NetworkManager/dispatcher.d/20-chrony
%{_sysconfdir}/dhcp/dhclient.d/chrony.sh
%{_bindir}/chronyc
%{_sbindir}/chronyd
%{_libexecdir}/chrony-helper
%{_unitdir}/ntp-units.d/*.list
%{_unitdir}/chrony*.service
%{_mandir}/man[158]/%{name}*.[158]*
%dir %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony
%ghost %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony/drift
%ghost %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony/rtc
%dir %attr(-,chrony,chrony) %{_localstatedir}/log/chrony
