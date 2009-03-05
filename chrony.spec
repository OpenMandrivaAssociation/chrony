Summary:	Chrony clock synchronization program
Name:		chrony
Version:	1.23
Release:	%mkrel 5
URL:		http://chrony.sunsite.dk/index.php
License:	GPLv2
Group:		System/Configuration/Other
Source0:	ftp://chrony.sunsite.dk/projects/chrony/%{name}-%{version}.tar.gz
Patch0:		%{name}-1.23-fix.patch
Patch1:		%{name}-1.20-fix-chkconfig.patch
BuildRequires:	termcap-devel
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	texinfo
Requires(pre):	rpm-helper
Conflicts:	ntp
Conflicts:	openntpd
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
A pair of programs for keeping computer clocks accurate. chronyd is a
background (daemon) program and chronyc is a command-line interface to
it.  Time reference sources for chronyd can be RFC1305 NTP servers,
human (via keyboard and chronyc), and the computer's real-time clock
at boot time (Linux only).  chronyd can determine the rate at which
the computer gains or loses time and compensate for it whilst no
external reference is present.  chronyd's use of NTP servers can be
switched on and off (through chronyc) to support computers with
dial-up or intermittent access to the Internet. chronyd can also act
as an RFC1305-compatible NTP server.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1

%build
CFLAGS="%{optflags}" \
./configure --prefix=%{_prefix}
%make
%make info

%install
rm -rf %{buildroot}
install -m755 -d  %{buildroot}/var/log/chrony

install -m755 chronyd.init -D %{buildroot}%{_initrddir}/chronyd
install -m644 chrony.conf -D %{buildroot}%{_sysconfdir}/chrony.conf
install -m644 chrony.keys -D %{buildroot}%{_sysconfdir}/chrony.keys
install -m644 chrony.log -D %{buildroot}%{_sysconfdir}/logrotate.d/chrony

#make install

install -m755 -d %{buildroot}%{_bindir}
install -m755 -d %{buildroot}%{_sbindir} 
install -m755 chronyd %{buildroot}%{_sbindir}
install -m755 chronyc %{buildroot}%{_bindir}

install -m755 -d %{buildroot}%{_mandir}/man1
install -m755 -d %{buildroot}%{_mandir}/man8
install -m644 chrony.1 %{buildroot}%{_mandir}/man1
install -m644 chronyc.1 %{buildroot}%{_mandir}/man1
install -m644 chronyd.8 %{buildroot}%{_mandir}/man8

install -m755 -d %buildroot/%{_infodir}
install -m644 chrony.info %buildroot/%{_infodir}

%post 
%_install_info chrony.info
%_post_service chronyd

%postun
rm -f %{_sysconfdir}/chrony.drift %{_sysconfdir}/chrony.rtc

%preun
%_remove_install_info chrony.info
%_preun_service chronyd

%clean
rm -rf %{buildroot}

%files
%defattr (-,root,root)
%doc INSTALL README README.rh chrony.texi
%{_sbindir}/*
%{_bindir}/*
%dir /var/log/chrony
%config(noreplace) %{_initrddir}/chronyd
%config(noreplace) %{_sysconfdir}/chrony.conf
%config(noreplace) %{_sysconfdir}/chrony.keys
%config(noreplace) %{_sysconfdir}/logrotate.d/chrony
%{_infodir}/chrony.info*
%{_mandir}/man1/*
%{_mandir}/man8/*

