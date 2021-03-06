Name:       oasis
Version:    2.0.0
Release:    1
Prefix:     %{_prefix}
Summary:    OASIS package

Group:      Development/Libraries
License:    Apache 2.0
URL:        http://www.opensciencegrid.org

Source0:    %{name}-%{version}.tar.gz

BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:  noarch

Vendor:     Jose Caballero <jcaballero@bnl.gov>
Packager:   RACF <grid@rcf.rhic.bnl.gov>
Provides:   oasis
Obsoletes:  oasis-server

%description
%{summary}


Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
Requires(postun): initscripts

%prep
%setup

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%pre
#!/bin/bash  
#

f_create_oasis_account(){
    #
    # creates, if does not exist already, system account "oasis"
    # adding the sticky bit 
    # so everyone can write, but only each user
    # can delete her own content
    #

    id oasis &> /dev/null
    rc=$?
    if [ $rc -ne 0 ]; then
        useradd -r -m oasis
        chmod 1777 /home/oasis
    fi
}
f_create_oasis_account 


%post
#!/bin/bash  

f_chkconfig(){
    #
    # add oasis daemon to checkconfig
    # but set it off. It is up to the sys admin to turn it on.
    # NOTE: only if operation is "install", not if it is "update"
    #

    if [ $1 -eq 1 ]; then 
        chkconfig --add oasisd
        chkconfig oasisd off
    fi
}
f_chkconfig $1


%preun
#!/bin/bash  
#

f_stop_daemon(){
    #
    # stops the daemon
    #

    if [ $1 -eq 0 ]; then
        # $1 == 0 => uninstall
        # $1 == 1 => upgrade 

        service oasisd status 1>/dev/null
        rc=$?
        if [ $rc -eq 0 ]; then
            # daemon is running...
            service oasisd stop 1>/dev/null
        fi
    fi
}

f_clean_chkconfig(){
    #
    # delete oasis daemon to checkconfig
    #

    if [ $1 -eq 0 ]; then
        # $1 == 0 => uninstall
        # $1 == 1 => upgrade 
        chkconfig --del oasisd 1>/dev/null
    fi
}
f_stop_daemon $1
f_clean_chkconfig $1

%postun
#!/bin/bash  
#

f_restart_daemon(){
    #
    # checks if the daemon is running,
    # if so, re-start it
    #

    if [ $1 -eq 1 ]; then 
        #$1 == 1 => upgrade
        #$1 == 0 => uninstall 

        service oasisd condrestart >/dev/null 2>&1
}
f_restart_daemon $1


%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc CHANGELOG LICENSE README

