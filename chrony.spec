%define gitpatch git1ca844a
%define git 1
%define prel pre1

Name:		chrony
Version:	1.27
%if %git
Release:	0.%{?prel}%{?gitpatch}.1
%else
Release:	1
%endif
Summary:	An NTP client/server
Group:		System/Base
License:	GPLv2
URL:		http://chrony.tuxfamily.org
Source0:	http://download.tuxfamily.org/chrony/chrony-%{version}-%{?prel}.tar.gz
Source1:	chrony.conf
Source2:	chrony.keys
Source3:	chronyd.service
Source4:	chrony.helper
Source5:	chrony.logrotate
Source7:	chrony.nm-dispatcher
Source8:	chrony.dhclient
Source9:	chrony-wait.service
%{?gitpatch:Patch0: chrony-%{version}-%{?prel}%{gitpatch}.patch.gz}
BuildRequires:	libcap-devel
BuildRequires:	libedit-devel
BuildRequires:	bison
BuildRequires:	texinfo
Requires(pre):	shadow-utils
Requires(post):	systemd-units info chkconfig
Requires(preun):	systemd-units info
Requires(postun):	systemd-units

%description
A client/server for the Network Time Protocol, this program keeps your
computer's clock accurate. It was specially designed to support
systems with intermittent internet connections, but it also works well
in permanently connected environments. It can use also hardware reference
clocks, system real-time clock or manual input as time references.

%prep
%setup -q -n %{name}-%{version}-%{?prel}
%{?gitpatch:%patch0 -p1}

%{?gitpatch: echo %{version}-%{gitpatch} > version.txt}

%build
%if %mdkver >= 201200
%serverbuild_hardened
%else
%serverbuild
export CFLAGS="$CFLAGS -pie -fpie"
export LDFLAGS="$LDFLAGS -Wl,-z,relro,-z,now"
%endif

%configure \
        --docdir=%{_docdir} \
        --with-sendmail=%{_sbindir}/sendmail

%make getdate all docs

%install
%makeinstall_std install-docs DESTDIR=%{buildroot}

rm -rf %{buildroot}%{_docdir}

mkdir -p %{buildroot}%{_sysconfdir}/{sysconfig,logrotate.d}
mkdir -p %{buildroot}%{_localstatedir}/{lib,log}/chrony
mkdir -p %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d
mkdir -p %{buildroot}%{_sysconfdir}/dhcp/dhclient.d
mkdir -p %{buildroot}/usr/libexec/
mkdir -p %{buildroot}/lib/systemd/system

install -m 644 -p %{SOURCE1} %{buildroot}%{_sysconfdir}/chrony.conf
install -m 640 -p %{SOURCE2} %{buildroot}%{_sysconfdir}/chrony.keys
install -m 644 -p %{SOURCE3} %{buildroot}/lib/systemd/system/chronyd.service
install -m 755 -p %{SOURCE4} %{buildroot}/usr/libexec/chrony-helper
install -m 644 -p %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/chrony
install -m 755 -p %{SOURCE7} %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/20-chrony
install -m 755 -p %{SOURCE8} %{buildroot}%{_sysconfdir}/dhcp/dhclient.d/chrony.sh
install -m 644 -p %{SOURCE9} %{buildroot}/lib/systemd/system/chrony-wait.service

touch %{buildroot}%{_localstatedir}/lib/chrony/{drift,rtc}

%pre
getent group chrony > /dev/null || /usr/sbin/groupadd -r chrony
getent passwd chrony > /dev/null || /usr/sbin/useradd -r -g chrony -d %{_localstatedir}/lib/chrony -s /sbin/nologin chrony
:

%post
/bin/systemctl daemon-reload &> /dev/null
:

%triggerun -- chrony < 1.25
if /sbin/chkconfig --level 3 chronyd; then
        /bin/systemctl enable chronyd.service &> /dev/null
fi
:

%preun
if [ "$1" -eq 0 ]; then
        /bin/systemctl --no-reload disable chrony-wait.service chronyd.service &> /dev/null
        /bin/systemctl stop chrony-wait.service chronyd.service &> /dev/null
fi
:

%postun
/bin/systemctl daemon-reload &> /dev/null
if [ "$1" -ge 1 ]; then
        /bin/systemctl try-restart chronyd.service &> /dev/null
fi
:

%files
%doc COPYING NEWS README chrony.txt faq.txt examples/*
%config(noreplace) %{_sysconfdir}/chrony.conf
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,chrony) %{_sysconfdir}/chrony.keys
%config(noreplace) %{_sysconfdir}/logrotate.d/chrony
%{_sysconfdir}/NetworkManager/dispatcher.d/20-chrony
%{_sysconfdir}/dhcp/dhclient.d/chrony.sh
%{_bindir}/chronyc
%{_sbindir}/chronyd
/usr/libexec/chrony-helper
%{_infodir}/chrony.info*
/lib/systemd/system/chrony*.service
%{_mandir}/man[158]/%{name}*.[158]*
%dir %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony
%ghost %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony/drift
%ghost %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony/rtc
%dir %attr(-,chrony,chrony) %{_localstatedir}/log/chrony
